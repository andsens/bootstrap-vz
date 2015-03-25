from image import Image
import logging
from contextlib import contextmanager
log = logging.getLogger(__name__)


def initialize_image(manifest, credentials, bootstrap_info):
	from boto.ec2 import connect_to_region
	connection = connect_to_region(bootstrap_info._ec2['region'],
	                               aws_access_key_id=credentials['access-key'],
	                               aws_secret_access_key=credentials['secret-key'])
	ami = connection.get_image(bootstrap_info._ec2['image'])
	image = AmazonMachineImage(manifest, ami)
	return image


class AmazonMachineImage(Image):

	def __init__(self, manifest, ami):
		super(AmazonMachineImage, self).__init__(manifest)
		self.ami = ami

	def destroy(self):
		log.debug('Deleting AMI')
		self.ami.deregister(delete_snapshot=True)
		del self.ami

	@contextmanager
	def get_instance(self, instance_type):
		from ..instances.ec2 import boot_image
		name = 'bootstrap-vz test instance'
		with boot_image(name, self.ami, instance_type) as instance:
			yield instance
