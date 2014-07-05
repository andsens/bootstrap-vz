from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.exceptions import TaskError
from bootstrapvz.common.tools import log_check_call
from ebs import Snapshot
from bootstrapvz.common.tasks import workspace
from connection import Connect
from . import assets
import os.path

cert_ec2 = os.path.join(assets, 'certs/cert-ec2.pem')


class AMIName(Task):
	description = 'Determining the AMI name'
	phase = phases.preparation
	predecessors = [Connect]

	@classmethod
	def run(cls, info):
		ami_name = info.manifest.image['name'].format(**info.manifest_vars)
		ami_description = info.manifest.image['description'].format(**info.manifest_vars)

		images = info._ec2['connection'].get_all_images(owners=['self'])
		for image in images:
			if ami_name == image.name:
				msg = 'An image by the name {ami_name} already exists.'.format(ami_name=ami_name)
				raise TaskError(msg)
		info._ec2['ami_name'] = ami_name
		info._ec2['ami_description'] = ami_description


class BundleImage(Task):
	description = 'Bundling the image'
	phase = phases.image_registration

	@classmethod
	def run(cls, info):
		bundle_name = 'bundle-' + info.run_id
		info._ec2['bundle_path'] = os.path.join(info.workspace, bundle_name)
		arch = {'i386': 'i386', 'amd64': 'x86_64'}.get(info.manifest.system['architecture'])
		log_check_call(['euca-bundle-image',
		                '--image', info.volume.image_path,
		                '--arch', arch,
		                '--user', info.credentials['user-id'],
		                '--privatekey', info.credentials['private-key'],
		                '--cert', info.credentials['certificate'],
		                '--ec2cert', cert_ec2,
		                '--destination', info._ec2['bundle_path'],
		                '--prefix', info._ec2['ami_name']])


class UploadImage(Task):
	description = 'Uploading the image bundle'
	phase = phases.image_registration
	predecessors = [BundleImage]

	@classmethod
	def run(cls, info):
		manifest_file = os.path.join(info._ec2['bundle_path'], info._ec2['ami_name'] + '.manifest.xml')
		if info._ec2['region'] == 'us-east-1':
			s3_url = 'https://s3.amazonaws.com/'
		elif info._ec2['region'] == 'cn-north-1':
			s3_url = 'https://s3.cn-north-1.amazonaws.com.cn'
		else:
			s3_url = 'https://s3-{region}.amazonaws.com/'.format(region=info._ec2['region'])
		info._ec2['manifest_location'] = info.manifest.image['bucket'] + '/' + info._ec2['ami_name'] + '.manifest.xml'
		log_check_call(['euca-upload-bundle',
		                '--bucket', info.manifest.image['bucket'],
		                '--manifest', manifest_file,
		                '--access-key', info.credentials['access-key'],
		                '--secret-key', info.credentials['secret-key'],
		                '--url', s3_url,
		                '--region', info._ec2['region'],
		                '--ec2cert', cert_ec2])


class RemoveBundle(Task):
	description = 'Removing the bundle files'
	phase = phases.cleaning
	successors = [workspace.DeleteWorkspace]

	@classmethod
	def run(cls, info):
		from shutil import rmtree
		rmtree(info._ec2['bundle_path'])
		del info._ec2['bundle_path']


class RegisterAMI(Task):
	description = 'Registering the image as an AMI'
	phase = phases.image_registration
	predecessors = [Snapshot, UploadImage]

	@classmethod
	def run(cls, info):
		registration_params = {'name': info._ec2['ami_name'],
		                       'description': info._ec2['ami_description']}
		registration_params['architecture'] = {'i386': 'i386',
		                                       'amd64': 'x86_64'}.get(info.manifest.system['architecture'])

		if info.manifest.volume['backing'] == 's3':
			registration_params['image_location'] = info._ec2['manifest_location']
		else:
			root_dev_name = {'pvm': '/dev/sda',
			                 'hvm': '/dev/xvda'}.get(info.manifest.provider['virtualization'])
			registration_params['root_device_name'] = root_dev_name

			from boto.ec2.blockdevicemapping import BlockDeviceType
			from boto.ec2.blockdevicemapping import BlockDeviceMapping
			block_device = BlockDeviceType(snapshot_id=info._ec2['snapshot'].id, delete_on_termination=True,
			                               size=info.volume.size.get_qty_in('GiB'))
			registration_params['block_device_map'] = BlockDeviceMapping()
			registration_params['block_device_map'][root_dev_name] = block_device

		if info.manifest.provider['virtualization'] == 'hvm':
			registration_params['virtualization_type'] = 'hvm'
		else:
			registration_params['virtualization_type'] = 'paravirtual'
			akis_path = os.path.join(os.path.dirname(__file__), 'ami-akis.yml')
			from bootstrapvz.common.tools import config_get
			registration_params['kernel_id'] = config_get(akis_path, [info._ec2['region'],
			                                                          info.manifest.system['architecture']])

		info._ec2['image'] = info._ec2['connection'].register_image(**registration_params)
