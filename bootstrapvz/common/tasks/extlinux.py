from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import apt
import filesystem
from bootstrapvz.base.fs import partitionmaps
import os.path


class AddExtlinuxPackage(Task):
	description = 'Adding extlinux package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('extlinux')
		if isinstance(info.volume.partition_map, partitionmaps.gpt.GPTPartitionMap):
			info.packages.add('syslinux-common')


class ConfigureExtlinux(Task):
	description = 'Configuring extlinux'
	phase = phases.system_modification
	predecessors = [filesystem.FStab]

	@classmethod
	def run(cls, info):
		if info.release_codename == 'squeeze':
			# On squeeze /etc/default/extlinux is generated when running extlinux-update
			log_check_call(['chroot', info.root,
			                'extlinux-update'])
		from bootstrapvz.common.tools import sed_i
		extlinux_def = os.path.join(info.root, 'etc/default/extlinux')
		sed_i(extlinux_def, r'^EXTLINUX_PARAMETERS="([^"]+)"$',
		                    r'EXTLINUX_PARAMETERS="\1 console=ttyS0"')


class InstallExtlinux(Task):
	description = 'Installing extlinux'
	phase = phases.system_modification
	predecessors = [filesystem.FStab, ConfigureExtlinux]

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
