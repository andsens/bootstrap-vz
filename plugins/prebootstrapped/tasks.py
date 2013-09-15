from base import Task
from common import phases
from providers.ec2.tasks import ebs
from common.tasks import volume
from common.tasks import bootstrap
import time
import logging
log = logging.getLogger(__name__)


class Snapshot(ebs.Snapshot):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap]

	def run(self, info):
		super(Snapshot, self).run(info)
		msg = 'A snapshot of the bootstrapped volume was created. ID: {id}'.format(id=info.snapshot.id)
		log.info(msg)


class CreateFromSnapshot(Task):
	description = 'Creating EBS volume from a snapshot'
	phase = phases.volume_creation
	before = [volume.Attach]

	def run(self, info):
		volume_size = int(info.manifest.volume['size'] / 1024)
		snapshot = info.manifest.plugins['prebootstrapped']['snapshot']
		info.volume.volume = info.connection.create_volume(volume_size,
		                                                   info.host['availabilityZone'],
		                                                   snapshot=snapshot)
		while info.volume.volume_state() != 'available':
			time.sleep(5)
			info.volume.update()

		info.volume.force_state('detached_fmt')
		partitions_state = 'formatted'
		if 'partitions' in info.manifest.volume:
			partitions_state = 'unmapped_fmt'
		for partition in info.volume.partition_map.partitions:
			partition.force_state(partitions_state)


class CopyImage(Task):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap]

	def run(self, info):
		import os.path
		from shutil import copyfile
		loopback_backup_name = 'loopback-{id:x}.img.backup'.format(id=info.run_id)
		destination = os.path.join(info.manifest.bootstrapper['workspace'], loopback_backup_name)
		copyfile(info.volume.image_path, destination)
		msg = 'A copy of the bootstrapped volume was created. Path: {path}'.format(path=destination)
		log.info(msg)


class CreateFromImage(Task):
	description = 'Creating loopback image from a copy'
	phase = phases.volume_creation
	before = [volume.Attach]

	def run(self, info):
		import os.path
		from shutil import copyfile
		info.volume.image_path = os.path.join(info.workspace, 'volume.{ext}'.format(ext=info.volume.extension))
		loopback_backup_path = info.manifest.plugins['prebootstrapped']['image']
		copyfile(loopback_backup_path, info.volume.image_path)

		info.volume.force_state('detached_fmt')
		partitions_state = 'formatted'
		if 'partitions' in info.manifest.volume:
			partitions_state = 'unmapped_fmt'
		for partition in info.volume.partition_map.partitions:
			partition.force_state(partitions_state)
