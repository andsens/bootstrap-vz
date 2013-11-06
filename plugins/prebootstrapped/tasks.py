from base import Task
from common import phases
from common.tasks import volume
from common.tasks import bootstrap
from common.tasks import filesystem
from common.fs import remount
from shutil import copyfile
import os.path
import time
import logging
log = logging.getLogger(__name__)


class Snapshot(Task):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap, filesystem.MountSpecials]

	def run(self, info):
		def mk_snapshot():
			return info.volume.snapshot()
		snapshot = remount(info.volume, mk_snapshot)
		msg = 'A snapshot of the bootstrapped volume was created. ID: {id}'.format(id=snapshot.id)
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

		set_fs_states(info.volume)


class CopyImage(Task):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap, filesystem.MountSpecials]

	def run(self, info):
		loopback_backup_name = 'volume-{id:x}.{ext}.backup'.format(id=info.run_id, ext=info.volume.extension)
		destination = os.path.join(info.manifest.bootstrapper['workspace'], loopback_backup_name)

		def mk_snapshot():
			copyfile(info.volume.image_path, destination)
		remount(info.volume, mk_snapshot)
		msg = 'A copy of the bootstrapped volume was created. Path: {path}'.format(path=destination)
		log.info(msg)


class CreateFromImage(Task):
	description = 'Creating loopback image from a copy'
	phase = phases.volume_creation
	before = [volume.Attach]

	def run(self, info):
		info.volume.image_path = os.path.join(info.workspace, 'volume.{ext}'.format(ext=info.volume.extension))
		loopback_backup_path = info.manifest.plugins['prebootstrapped']['image']
		copyfile(loopback_backup_path, info.volume.image_path)

		set_fs_states(info.volume)


class SetBootMountDir(Task):
	description = 'Setting mountpoint for the boot partition'
	phase = phases.volume_mounting
	after = [filesystem.MountRoot]
	before = [filesystem.MountBoot]

	def run(self, info):
		info.boot_dir = os.path.join(info.root, 'boot')


def set_fs_states(volume):
		volume.fsm.current = 'detached'

		p_map = volume.partition_map
		partitions_state = 'attached'
		from base.fs.partitionmaps.none import NoPartitions
		if isinstance(p_map, NoPartitions):
			partitions_state = 'formatted'
		else:
			p_map.fsm.current = 'unmapped'
			partitions_state = 'unmapped_fmt'
		for partition in p_map.partitions:
			partition.fsm.current = partitions_state
