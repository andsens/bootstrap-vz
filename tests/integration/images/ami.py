from image import Image
import logging
from contextlib import contextmanager
log = logging.getLogger(__name__)


def initialize_image(manifest, credentials, bootstrap_info):
	from boto.ec2 import connect_to_region
	connection = connect_to_region(bootstrap_info._ec2['region'],
	                               aws_access_key_id=credentials['access-key'],
	                               aws_secret_access_key=credentials['secret-key'])
	image = AmazonMachineImage(manifest, bootstrap_info._ec2['image'], connection)
	return image


class AmazonMachineImage(Image):

	def __init__(self, manifest, image_id, connection):
		super(AmazonMachineImage, self).__init__(manifest)
		self.ami = connection.get_image(image_id)
		self.connection = connection

	def destroy(self):
		log.debug('Deleting AMI')
		self.ami.deregister()
		for device, block_device_type in self.ami.block_device_mapping.items():
			self.connection.delete_snapshot(block_device_type.snapshot_id)
		del self.ami

	@contextmanager
	def get_instance(self, instance_type):
		from ..instances.ec2 import boot_image
		name = 'bootstrap-vz test instance'
		with boot_image(name, self.ami, instance_type) as instance:
			yield instance
