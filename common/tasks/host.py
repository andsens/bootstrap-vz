from base import Task
from common import phases
from common.exceptions import TaskError


class HostDependencies(Task):
	description = 'Determining required host dependencies'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		info.host_dependencies.add('debootstrap')

		from common.fs.loopbackvolume import LoopbackVolume
		if isinstance(info.volume, LoopbackVolume):
			info.host_dependencies.add('qemu-utils')

		if 'xfs' in (p.filesystem for p in info.volume.partition_map.partitions):
			info.host_dependencies.add('xfsprogs')

		from base.fs.partitionmaps.none import NoPartitions
		if not isinstance(info.volume.partition_map, NoPartitions):
			info.host_dependencies.update(['parted', 'kpartx'])


class CheckHostDependencies(Task):
	description = 'Checking installed host packages'
	phase = phases.preparation
	predecessors = [HostDependencies]

	@classmethod
	def run(cls, info):
		from common.tools import log_check_call
		from subprocess import CalledProcessError
		for package in info.host_dependencies:
			try:
				log_check_call(['/usr/bin/dpkg-query', '-s', package])
			except CalledProcessError:
				msg = "The package `{0}\' is not installed".format(package)
				raise TaskError(msg)
