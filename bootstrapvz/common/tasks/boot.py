from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import apt
import filesystem
from bootstrapvz.base.fs import partitionmaps
import os.path


class UpdateInitramfs(Task):
	description = 'Updating initramfs'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from ..tools import log_check_call
		log_check_call(['chroot', info.root, 'update-initramfs', '-u'])


class BlackListModules(Task):
	description = 'Blacklisting kernel modules'
	phase = phases.system_modification
	successors = [UpdateInitramfs]

	@classmethod
	def run(cls, info):
		blacklist_path = os.path.join(info.root, 'etc/modprobe.d/blacklist.conf')
		with open(blacklist_path, 'a') as blacklist:
			blacklist.write(('# disable pc speaker and floppy\n'
			                 'blacklist pcspkr\n'
			                 'blacklist floppy\n'))


class DisableGetTTYs(Task):
	description = 'Disabling getty processes'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from ..tools import sed_i
		inittab_path = os.path.join(info.root, 'etc/inittab')
		tty1 = '1:2345:respawn:/sbin/getty 38400 tty1'
		sed_i(inittab_path, '^' + tty1, '#' + tty1)
		ttyx = ':23:respawn:/sbin/getty 38400 tty'
		for i in range(2, 7):
			i = str(i)
			sed_i(inittab_path, '^' + i + ttyx + i, '#' + i + ttyx + i)


class AddGrubPackage(Task):
	description = 'Adding grub package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('grub-pc')


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification
	predecessors = [filesystem.FStab]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		grub_def = os.path.join(info.root, 'etc/default/grub')
		sed_i(grub_def, '^#GRUB_TERMINAL=console', 'GRUB_TERMINAL=console')
		sed_i(grub_def, '^GRUB_CMDLINE_LINUX_DEFAULT="quiet"',
		                'GRUB_CMDLINE_LINUX_DEFAULT="console=ttyS0"')


class InstallGrub_1_99(Task):
	description = 'Installing grub 1.99'
	phase = phases.system_modification
	predecessors = [filesystem.FStab]

	@classmethod
	def run(cls, info):

		from ..fs import remount
		p_map = info.volume.partition_map

		def link_fn():
			info.volume.link_dm_node()
			if isinstance(p_map, partitionmaps.none.NoPartitions):
				p_map.root.device_path = info.volume.device_path

		def unlink_fn():
			info.volume.unlink_dm_node()
			if isinstance(p_map, partitionmaps.none.NoPartitions):
				p_map.root.device_path = info.volume.device_path

		# GRUB cannot deal with installing to loopback devices
		# so we fake a real harddisk with dmsetup.
		# Guide here: http://ebroder.net/2009/08/04/installing-grub-onto-a-disk-image/
		from ..fs.loopbackvolume import LoopbackVolume
		if isinstance(info.volume, LoopbackVolume):
			remount(info.volume, link_fn)
		try:
			[device_path] = log_check_call(['readlink', '-f', info.volume.device_path])
			device_map_path = os.path.join(info.root, 'boot/grub/device.map')
			partition_prefix = 'msdos'
			if isinstance(p_map, partitionmaps.gpt.GPTPartitionMap):
				partition_prefix = 'gpt'
			with open(device_map_path, 'w') as device_map:
				device_map.write('(hd0) {device_path}\n'.format(device_path=device_path))
				if not isinstance(p_map, partitionmaps.none.NoPartitions):
					for idx, partition in enumerate(info.volume.partition_map.partitions):
						device_map.write('(hd0,{prefix}{idx}) {device_path}\n'
						                 .format(device_path=partition.device_path,
						                         prefix=partition_prefix,
						                         idx=idx + 1))

			# Install grub
			log_check_call(['chroot', info.root, 'grub-install', device_path])
			log_check_call(['chroot', info.root, 'update-grub'])
		except Exception as e:
			if isinstance(info.volume, LoopbackVolume):
				remount(info.volume, unlink_fn)
			raise e

		if isinstance(info.volume, LoopbackVolume):
			remount(info.volume, unlink_fn)


class InstallGrub_2(Task):
	description = 'Installing grub 2'
	phase = phases.system_modification
	predecessors = [filesystem.FStab]

	@classmethod
	def run(cls, info):
		log_check_call(['chroot', info.root, 'grub-install', info.volume.device_path])
		log_check_call(['chroot', info.root, 'update-grub'])


class AddExtlinuxPackage(Task):
	description = 'Adding extlinux package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('extlinux')
		if isinstance(info.volume.partition_map, partitionmaps.gpt.GPTPartitionMap):
			info.packages.add('syslinux-common')


class ConfigureExtLinux(Task):
	description = 'Configuring extlinux'
	phase = phases.system_modification
	predecessors = [filesystem.FStab]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		extlinux_def = os.path.join(info.root, 'etc/default/extlinux')
		sed_i(extlinux_def, '^EXTLINUX_PARAMETERS="ro quiet"',
		                    'EXTLINUX_PARAMETERS="ro console=ttyS0"')


class InstallExtLinux(Task):
	description = 'Installing extlinux'
	phase = phases.system_modification
	predecessors = [filesystem.FStab]

	@classmethod
	def run(cls, info):
		if isinstance(info.volume.partition_map, partitionmaps.gpt.GPTPartitionMap):
			bootloader = '/usr/lib/syslinux/gptmbr.bin'
		else:
			bootloader = '/usr/lib/extlinux/mbr.bin'
		log_check_call(['chroot', info.root,
		                'dd', 'bs=440', 'count=1',
		                'if=' + bootloader,
		                'of=' + info.volume.device_path])
		log_check_call(['chroot', info.root,
		                'extlinux',
		                '--install', '/boot/extlinux'])
		log_check_call(['chroot', info.root,
		                'extlinux-update'])
