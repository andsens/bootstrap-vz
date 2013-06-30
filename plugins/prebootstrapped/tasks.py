from base import Task
from common import phases
from providers.ec2.tasks import connection
from providers.ec2.tasks import ebs
import time


class CreateVolumeFromSnapshot(Task):
	phase = phases.volume_creation
	after = [connection.Connect]
	before = [ebs.AttachVolume]

	description = 'Creating EBS volume from a snapshot'

	def run(self, info):
		volume_size = int(info.manifest.volume['size']/1024)
		snapshot = info.manifest.plugins['prebootstrapped']['snapshot']
		info.volume = info.connection.create_volume(volume_size,
		                                            info.host['availabilityZone'],
		                                            snapshot=snapshot)
		while info.volume.volume_state() != 'available':
			time.sleep(5)
			info.volume.update()
