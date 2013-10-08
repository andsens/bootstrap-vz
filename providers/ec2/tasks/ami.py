from base import Task
from common import phases
from common.exceptions import TaskError
from common.tools import log_check_call
from ebs import Snapshot
from common.tasks import workspace
from connection import Connect
import os.path

cert_ec2 = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/certs/cert-ec2.pem'))


class AMIName(Task):
	description = 'Determining the AMI name'
	phase = phases.preparation
	after = [Connect]

	def run(self, info):
		image_vars = {'release':        info.manifest.system['release'],
		              'architecture':   info.manifest.system['architecture'],
		              'virtualization': info.manifest.virtualization,
		              'backing':        info.manifest.volume['backing']}
		from datetime import datetime
		now = datetime.now()
		time_vars = ['%a', '%A', '%b', '%B', '%c', '%d', '%f', '%H',
		             '%I', '%j', '%m', '%M', '%p', '%S', '%U', '%w',
		             '%W', '%x', '%X', '%y', '%Y', '%z', '%Z']
		for var in time_vars:
			image_vars[var] = now.strftime(var)

		ami_name = info.manifest.image['name'].format(**image_vars)
		ami_description = info.manifest.image['description'].format(**image_vars)

		images = info.connection.get_all_images()
		for image in images:
			if ami_name == image.name:
				msg = 'An image by the name {ami_name} already exists.'.format(ami_name=ami_name)
				raise TaskError(msg)
		info.ami_name = ami_name
		info.ami_description = ami_description


class BundleImage(Task):
	description = 'Bundling the image'
	phase = phases.image_registration

	def run(self, info):
		bundle_name = 'bundle-{id:x}'.format(id=info.run_id)
		info.bundle_path = os.path.join(info.workspace, bundle_name)
		log_check_call(['/usr/bin/euca-bundle-image',
		                '--image', info.loopback_file,
		                '--user', info.credentials['user-id'],
		                '--privatekey', info.credentials['private-key'],
		                '--cert', info.credentials['certificate'],
		                '--ec2cert', cert_ec2,
		                '--destination', info.bundle_path,
		                '--prefix', info.ami_name])


class UploadImage(Task):
	description = 'Uploading the image bundle'
	phase = phases.image_registration
	after = [BundleImage]

	def run(self, info):
		manifest_file = os.path.join(info.bundle_path, info.ami_name + '.manifest.xml')
		if info.host['region'] == 'us-east-1':
			s3_url = 'https://s3.amazonaws.com/'
		else:
			s3_url = 'https://s3-{region}.amazonaws.com/'.format(region=info.host['region'])
		log_check_call(['/usr/bin/euca-upload-bundle',
		                '--bucket', info.manifest.image['bucket'],
		                '--manifest', manifest_file,
		                '--access-key', info.credentials['access-key'],
		                '--secret-key', info.credentials['secret-key'],
		                '--url', s3_url,
		                '--region', info.host['region'],
		                '--ec2cert', cert_ec2])


class RemoveBundle(Task):
	description = 'Removing the bundle files'
	phase = phases.cleaning
	before = [workspace.DeleteWorkspace]

	def run(self, info):
		from shutil import rmtree
		rmtree(info.bundle_path)
		del info.bundle_path


class RegisterAMI(Task):
	description = 'Registering the image as an AMI'
	phase = phases.image_registration
	after = [Snapshot, UploadImage]

	kernel_mapping = {'us-east-1':      {'amd64': 'aki-88aa75e1',
	                                     'i386':  'aki-b6aa75df'},
	                  'us-west-1':      {'amd64': 'aki-f77e26b2',
	                                     'i386':  'aki-f57e26b0'},
	                  'us-west-2':      {'amd64': 'aki-fc37bacc',
	                                     'i386':  'aki-fa37baca'},
	                  'eu-west-1':      {'amd64': 'aki-71665e05',
	                                     'i386':  'aki-75665e01'},
	                  'ap-southeast-1': {'amd64': 'aki-fe1354ac',
	                                     'i386':  'aki-f81354aa'},
	                  'ap-southeast-2': {'amd64': 'aki-31990e0b',
	                                     'i386':  'aki-33990e09'},
	                  'ap-northeast-1': {'amd64': 'aki-44992845',
	                                     'i386':  'aki-42992843'},
	                  'sa-east-1':      {'amd64': 'aki-c48f51d9',
	                                     'i386':  'aki-ca8f51d7'},
	                  'us-gov-west-1':  {'amd64': 'aki-79a4c05a',
	                                     'i386':  'aki-7ba4c058'}}

	def run(self, info):
		arch = {'i386': 'i386', 'amd64': 'x86_64'}.get(info.manifest.system['architecture'])
		kernel_id = self.kernel_mapping.get(info.host['region']).get(info.manifest.system['architecture'])

		from providers.ec2.ebsvolume import EBSVolume
		from common.fs.loopbackvolume import LoopbackVolume

		if isinstance(info.volume, EBSVolume):
			from boto.ec2.blockdevicemapping import BlockDeviceType
			from boto.ec2.blockdevicemapping import BlockDeviceMapping
			block_device = BlockDeviceType(snapshot_id=info.snapshot.id, delete_on_termination=True,
			                               size=info.volume.partition_map.get_total_size()/1024)
			block_device_map = BlockDeviceMapping()
			block_device_map['/dev/sda1'] = block_device

			info.image = info.connection.register_image(name=info.ami_name, description=info.ami_description,
			                                            architecture=arch, kernel_id=kernel_id,
			                                            root_device_name='/dev/sda1',
			                                            block_device_map=block_device_map)
		if isinstance(info.volume, LoopbackVolume):
			image_location = ('{bucket}/{ami_name}.manifest.xml'
			                  .format(bucket=info.manifest.image['bucket'],
			                          ami_name=info.ami_name))
			info.image = info.connection.register_image(description=info.ami_description,
			                                            architecture=arch, kernel_id=kernel_id,
			                                            root_device_name='/dev/sda1',
			                                            image_location=image_location)
