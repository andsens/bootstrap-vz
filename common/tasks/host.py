from base import Task
from common import phases
from common.exceptions import TaskError


class AddExternalCommands(Task):
	description = 'Determining which external commands are required'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		info.host_dependencies['debootstrap'] = 'debootstrap'

		from common.fs.loopbackvolume import LoopbackVolume
		if isinstance(info.volume, LoopbackVolume):
			info.host_dependencies['qemu-img'] = 'qemu-utils'
			info.host_dependencies['losetup'] = 'mount'
		from common.fs.qemuvolume import QEMUVolume
		if isinstance(info.volume, QEMUVolume):
			info.host_dependencies['losetup'] = 'qemu-nbd'

		if 'xfs' in (p.filesystem for p in info.volume.partition_map.partitions):
			info.host_dependencies['mkfs.xfs'] = 'xfsprogs'

		from base.fs.partitionmaps.none import NoPartitions
		if not isinstance(info.volume.partition_map, NoPartitions):
			info.host_dependencies['parted'] = 'parted'
			info.host_dependencies['kpartx'] = 'kpartx'


class CheckExternalCommands(Task):
	description = 'Checking availability of external commands'
	phase = phases.preparation
	predecessors = [AddExternalCommands]

	@classmethod
	def run(cls, info):
		from common.tools import log_check_call
		from subprocess import CalledProcessError
		missing_packages = []
		for command, package in info.host_dependencies.items():
			try:
				log_check_call(['type ' + command], shell=True)
			except CalledProcessError:
				msg = ('The command `{command}\' is not available, '
				       'it is located in the package `{package}\'.'
				       .format(command=command, package=package))
				missing_packages.append(msg)
		if len(missing_packages) > 0:
			msg = '\n'.join(missing_packages)
			raise TaskError(msg)
