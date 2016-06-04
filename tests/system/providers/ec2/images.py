import logging
log = logging.getLogger(__name__)


class AmazonMachineImage(object):

    def __init__(self, image_id, ec2_connection):
        self.ec2_connection = ec2_connection
        self.ami = self.ec2_connection.get_image(image_id)


class EBSImage(AmazonMachineImage):

    def destroy(self):
        log.debug('Deleting AMI')
        self.ami.deregister()
        for device, block_device_type in self.ami.block_device_mapping.items():
            self.ec2_connection.delete_snapshot(block_device_type.snapshot_id)
        del self.ami


class S3Image(AmazonMachineImage):

    def destroy(self):
        log.debug('Deleting AMI')
        self.ami.deregister()
        del self.ami
