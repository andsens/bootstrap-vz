from base import Task
from common import phases
from ebs import CreateSnapshot
from connection import Connect
from common.exceptions import TaskError


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


class RegisterAMI(Task):
	description = 'Registering the image as an AMI'
	phase = phases.image_registration
	after = [CreateSnapshot]

	def run(self, info):
		arch = {'i386': 'i386',
		        'amd64': 'x86_64'}.get(info.manifest.system['architecture'])
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
		kernel_id = kernel_mapping.get(info.host['region']).get(info.manifest.system['architecture'])

		from boto.ec2.blockdevicemapping import BlockDeviceType
		from boto.ec2.blockdevicemapping import BlockDeviceMapping
		block_device = BlockDeviceType(snapshot_id=info.snapshot.id, delete_on_termination=True,
		                               size=info.manifest.ebs_volume_size)
		block_device_map = BlockDeviceMapping()
		block_device_map['/dev/sda1'] = block_device

		info.image = info.connection.register_image(name=info.ami_name, description=info.ami_description,
		                                            architecture=arch, kernel_id=kernel_id,
		                                            root_device_name='/dev/sda1',
		                                            block_device_map=block_device_map)
