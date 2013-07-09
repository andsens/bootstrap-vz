from base import Task
from common import phases
from providers.ec2.tasks import connection
from providers.ec2.tasks import ebs
from providers.ec2.tasks import bootstrap
import time
import logging
log = logging.getLogger(__name__)


class CreateVolumeFromSnapshot(Task):
	description = 'Creating EBS volume from a snapshot'
	phase = phases.volume_creation
	after = [connection.Connect]
	before = [ebs.AttachVolume]

	def run(self, info):
		volume_size = int(info.manifest.volume['size']/1024)
		snapshot = info.manifest.plugins['prebootstrapped']['snapshot']
		info.volume = info.connection.create_volume(volume_size,
		                                            info.host['availabilityZone'],
		                                            snapshot=snapshot)
		while info.volume.volume_state() != 'available':
			time.sleep(5)
			info.volume.update()


class CreateSnapshot(ebs.CreateSnapshot):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap]

	def run(self, info):
		super(CreateSnapshot, self).run(info)
		msg = 'A snapshot of the bootstrapped volume was created. ID: {id}'.format(id=info.snapshot.id)
		log.info(msg)
