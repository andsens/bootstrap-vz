from base import Task
from common import phases


class HostPackages(Task):
	description = 'Determining required host packages'
	phase = phases.preparation

	def run(self, info):
		info.host_packages = set()
		info.host_packages.add('debootstrap')

		from common.fs.loopbackvolume import LoopbackVolume
		if isinstance(info.volume, LoopbackVolume):
			info.host_packages.add('qemu-utils')

		if 'xfs' in (p.filesystem for p in info.volume.partition_map.partitions):
			info.host_packages.add('xfsprogs')

		from base.fs.partitionmaps.none import NoPartitions
		if not isinstance(info.volume.partition_map, NoPartitions):
			info.host_packages.update(['parted', 'kpartx'])


class ImagePackages(Task):
	description = 'Determining required image packages'
	phase = phases.preparation

	def run(self, info):
		info.img_packages = set(), set()
		include, exclude = info.img_packages
		# We could bootstrap without locales, but things just suck without them, error messages etc.
		include.add('locales')
