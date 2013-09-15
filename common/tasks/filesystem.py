from base import Task
from common import phases
from common.tools import log_check_call
from bootstrap import Bootstrap
import volume


class Format(Task):
	description = 'Formatting the volume'
	phase = phases.volume_preparation

	def run(self, info):
		info.volume.format()


class TuneVolumeFS(Task):
	description = 'Tuning the bootstrap volume filesystem'
	phase = phases.volume_preparation
	after = [Format]

	def run(self, info):
		import re
		# Disable the time based filesystem check
		for partition in info.volume.partition_map.partitions:
			if re.match('^ext[2-4]$', partition.filesystem) is not None:
				log_check_call(['/sbin/tune2fs', '-i', '0', partition.device_path])


class AddXFSProgs(Task):
	description = 'Adding `xfsprogs\' to the image packages'
	phase = phases.preparation

	def run(self, info):
		include, exclude = info.img_packages
		include.add('xfsprogs')


class CreateMountDir(Task):
	description = 'Creating mountpoint for the root partition'
	phase = phases.volume_mounting

	def run(self, info):
		import os
		info.root = os.path.join(info.workspace, 'root')
		os.makedirs(info.root)


class MountRoot(Task):
	description = 'Mounting the root partition'
	phase = phases.volume_mounting
	after = [CreateMountDir]

	def run(self, info):
		info.volume.mount_root(info.root)


class MountBoot(Task):
	description = 'Mounting the boot partition'
	phase = phases.volume_mounting
	after = [MountRoot]

	def run(self, info):
		info.volume.mount_boot()


class CreateBootMountDir(Task):
	description = 'Creating mountpoint for the boot partition'
	phase = phases.volume_mounting
	after = [MountRoot]
	before = [MountBoot]

	def run(self, info):
		import os
		boot_dir = os.path.join(info.root, 'boot')
		os.makedirs(boot_dir)


class MountSpecials(Task):
	description = 'Mounting special block devices'
	phase = phases.os_installation
	after = [Bootstrap]

	def run(self, info):
		info.volume.mount_specials()


class UnmountRoot(Task):
	description = 'Unmounting the bootstrap volume'
	phase = phases.volume_unmounting
	before = [volume.Detach]

	def run(self, info):
		info.volume.unmount_root()


class UnmountBoot(Task):
	description = 'Unmounting the boot partition'
	phase = phases.volume_unmounting
	before = [UnmountRoot]

	def run(self, info):
		info.volume.unmount_boot()


class UnmountSpecials(Task):
	description = 'Unmunting special block devices'
	phase = phases.volume_unmounting
	before = [UnmountRoot]

	def run(self, info):
		info.volume.unmount_specials()


class DeleteMountDir(Task):
	description = 'Deleting mountpoint for the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountRoot]

	def run(self, info):
		import os
		os.rmdir(info.root)
		del info.root


class FStab(Task):
	description = 'Adding partitions to the fstab'
	phase = phases.system_modification

	def run(self, info):
		import os.path
		# device = '/dev/sda'
		# if info.manifest.virtualization == 'pvm':
		# 	device = '/dev/xvda'
		fstab_lines = []
		for mount_point, partition in info.volume.partition_map.mount_points:
			mount_opts = ['defaults']
			if partition.filesystem in ['ext2', 'ext3', 'ext4']:
				mount_opts.append('barrier=0')
			if partition.filesystem == 'xfs':
				mount_opts.append('nobarrier')
			fstab_lines.append('UUID={uuid} {mountpoint} {filesystem} {mount_opts} 1 1'
			                   .format(uuid=partition.get_uuid(),
			                           mountpoint=mount_point,
			                           filesystem=partition.filesystem,
			                           mount_opts=','.join(mount_opts)))

		fstab_path = os.path.join(info.root, 'etc/fstab')
		with open(fstab_path, 'w') as fstab:
			fstab.write('\n'.join(fstab_lines))
