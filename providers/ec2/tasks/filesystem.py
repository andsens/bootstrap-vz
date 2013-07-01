from base import Task
from common import phases
from common.exceptions import TaskError
from common.tools import log_check_call
from bootstrap import Bootstrap
import logging
log = logging.getLogger(__name__)


class FormatVolume(Task):
	description = 'Formatting the volume'
	phase = phases.volume_preparation

	def run(self, info):
		dev_path = info.bootstrap_device['path']
		mkfs = '/sbin/mkfs.{fs}'.format(fs=info.manifest.volume['filesystem'])
		log_check_call([mkfs, dev_path], log)


class TuneVolumeFS(Task):
	description = 'Tuning the bootstrap volume filesystem'
	phase = phases.volume_preparation
	after = [FormatVolume]

	def run(self, info):
		dev_path = info.bootstrap_device['path']
		# Disable the time based filesystem check
		command = ['/sbin/tune2fs', '-i', '0', dev_path]
		log_check_call(command, log)


class AddXFSProgs(Task):
	description = 'Adding `xfsprogs\' to the image packages'
	phase = phases.preparation

	def run(self, info):
		include, exclude = info.img_packages
		include.add('xfsprogs')


class CreateMountDir(Task):
	description = 'Creating mountpoint for the bootstrap volume'
	phase = phases.volume_mounting

	def run(self, info):
		import os
		mount_dir = info.manifest.bootstrapper['mount_dir']
		info.root = '{mount_dir}/{vol_id}'.format(mount_dir=mount_dir, vol_id=info.volume.id)
		# Works recursively, fails if last part exists, which is exaclty what we want.
		os.makedirs(info.root)


class MountVolume(Task):
	description = 'Mounting the bootstrap volume'
	phase = phases.volume_mounting
	after = [CreateMountDir]

	def run(self, info):
		with open('/proc/mounts') as mounts:
			for mount in mounts:
				if info.root in mount:
					msg = 'Something is already mounted at {root}'.format(root=info.root)
					raise TaskError(msg)

		command = ['mount', info.bootstrap_device['path'], info.root]
		log_check_call(command, log)


class MountSpecials(Task):
	description = 'Mounting special block devices'
	phase = phases.os_installation
	after = [Bootstrap]

	def run(self, info):
		log_check_call(['mount', '--bind', '/dev', '{root}/dev'.format(root=info.root)], log)
		log_check_call(['chroot', info.root, 'mount', '-t', 'proc', 'none', '/proc'], log)
		log_check_call(['chroot', info.root, 'mount', '-t', 'sysfs', 'none', '/sys'], log)
		log_check_call(['chroot', info.root, 'mount', '-t', 'devpts', 'none', '/dev/pts'], log)


class UnmountSpecials(Task):
	description = 'Unmunting special block devices'
	phase = phases.volume_unmounting

	def run(self, info):
		log_check_call(['chroot', info.root, 'umount', '/dev/pts'], log)
		log_check_call(['chroot', info.root, 'umount', '/sys'], log)
		log_check_call(['chroot', info.root, 'umount', '/proc'], log)
		log_check_call(['umount', '{root}/dev'.format(root=info.root)], log)


class UnmountVolume(Task):
	description = 'Unmounting the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountSpecials]

	def run(self, info):
		log_check_call(['umount', info.root], log)


class DeleteMountDir(Task):
	description = 'Deleting mountpoint for the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountVolume]

	def run(self, info):
		import os
		os.rmdir(info.root)
		del info.root
