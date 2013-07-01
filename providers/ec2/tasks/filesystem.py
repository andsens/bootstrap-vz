from base import Task
from common import phases
from common.exceptions import TaskError
from common.tools import log_command
from bootstrap import Bootstrap
import subprocess
import os
import logging
log = logging.getLogger(__name__)


class FormatVolume(Task):
	description = 'Formatting the volume'
	phase = phases.volume_preparation

	def run(self, info):
		dev_path = info.bootstrap_device['path']
		mkfs = '/sbin/mkfs.{fs}'.format(fs=info.manifest.volume['filesystem'])
		with open(os.devnull, 'w') as dev_null:
			subprocess.check_call([mkfs, dev_path], stdout=dev_null, stderr=dev_null)


class TuneVolumeFS(Task):
	description = 'Tuning the bootstrap volume filesystem'
	phase = phases.volume_preparation
	after = [FormatVolume]

	def run(self, info):
		dev_path = info.bootstrap_device['path']
		# Disable the time based filesystem check
		with open(os.devnull, 'w') as dev_null:
			subprocess.check_call(['/sbin/tune2fs', '-i', '0', dev_path], stdout=dev_null, stderr=dev_null)


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

		dev_path = info.bootstrap_device['path']
		with open(os.devnull, 'w') as dev_null:
			subprocess.check_call(['mount', dev_path, info.root], stdout=dev_null, stderr=dev_null)


class MountSpecials(Task):
	description = 'Mounting special block devices'
	phase = phases.os_installation
	after = [Bootstrap]

	def run(self, info):
		if log_command(['mount', '--bind', '/dev', '{root}/dev'.format(root=info.root)], log) != 0:
			raise TaskError('Failed to bind /dev to {root}/dev'.format(root=info.root))
		if log_command(['chroot', info.root, 'mount', '-t', 'proc', 'none', '/proc'], log) != 0:
			raise TaskError('Failed to mount /proc')
		if log_command(['chroot', info.root, 'mount', '-t', 'sysfs', 'none', '/sys'], log) != 0:
			raise TaskError('Failed to mount /sys')
		if log_command(['chroot', info.root, 'mount', '-t', 'devpts', 'none', '/dev/pts'], log) != 0:
			raise TaskError('Failed to mount /dev/pts')


class UnmountSpecials(Task):
	description = 'Unmunting special block devices'
	phase = phases.volume_unmounting

	def run(self, info):
		if log_command(['chroot', info.root, 'umount', '/dev/pts'], log) != 0:
			raise TaskError('Failed to unmount /dev/pts')
		if log_command(['chroot', info.root, 'umount', '/sys'], log) != 0:
			raise TaskError('Failed to unmount /sys')
		if log_command(['chroot', info.root, 'umount', '/proc'], log) != 0:
			raise TaskError('Failed to unmount /proc')
		if log_command(['umount', '{root}/dev'.format(root=info.root)], log) != 0:
			raise TaskError('Failed to unmount /dev from {root}/dev'.format(root=info.root))


class UnmountVolume(Task):
	description = 'Unmounting the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountSpecials]

	def run(self, info):
		with open(os.devnull, 'w') as dev_null:
			subprocess.check_call(['umount', info.root], stdout=dev_null, stderr=dev_null)


class DeleteMountDir(Task):
	description = 'Deleting mountpoint for the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountVolume]

	def run(self, info):
		os.rmdir(info.root)
		del info.root
