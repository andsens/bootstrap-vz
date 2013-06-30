from base import Task
from common import phases
from connection import Connect
import time


class CreateVolumeFromSnapshot(Task):
	phase = phases.volume_creation
	after = [Connect]

	description = 'Creating an EBS volume from a snapshot'

	def run(self, info):
		volume_size = int(info.manifest.volume['size']/1024)
		snapshot_id = info.manifest.plugins['prebootstrapped'].snapshot_id
		info.volume = info.connection.create_volume(volume_size,
		                                            info.host['availabilityZone'],
		                                            snapshot=snapshot_id)
		while info.volume.volume_state() != 'available':
			time.sleep(5)
			info.volume.update()
