from image import Image
import logging
from contextlib import contextmanager
log = logging.getLogger(__name__)


def initialize_image(manifest, credentials, bootstrap_info):
	image = AmazonMachineImage(manifest, bootstrap_info._ec2['image'],
	                           bootstrap_info._ec2['region'], credentials)
	return image


class AmazonMachineImage(Image):

	def __init__(self, manifest, image_id, region, credentials):
		super(AmazonMachineImage, self).__init__(manifest)

		from boto.ec2 import connect_to_region as ec2_connect
		self.ec2_connection = ec2_connect(region, aws_access_key_id=credentials['access-key'],
		                                  aws_secret_access_key=credentials['secret-key'])
		from boto.vpc import connect_to_region as vpc_connect
		self.vpc_connection = vpc_connect(region, aws_access_key_id=credentials['access-key'],
		                                  aws_secret_access_key=credentials['secret-key'])

		self.ami = self.ec2_connection.get_image(image_id)

	def destroy(self):
		log.debug('Deleting AMI')
		self.ami.deregister()
		for device, block_device_type in self.ami.block_device_mapping.items():
			self.ec2_connection.delete_snapshot(block_device_type.snapshot_id)
		del self.ami

	@contextmanager
	def get_instance(self, instance_type):
		from ..instances.ec2 import boot_image
		with boot_image(self.ami, instance_type, self.ec2_connection, self.vpc_connection) as instance:
			yield instance
