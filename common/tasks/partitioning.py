from base import Task
from common import phases
import filesystem
import volume


class PartitionVolume(Task):
	description = 'Partitioning the volume'
	phase = phases.volume_preparation

	def run(self, info):
		info.volume.partition()


class MapPartitions(Task):
	description = 'Mapping volume partitions'
	phase = phases.volume_preparation
	before = [filesystem.Format]
	after = [PartitionVolume]

	def run(self, info):
		info.volume.map()


class UnmapPartitions(Task):
	description = 'Removing volume partitions mapping'
	phase = phases.volume_unmounting
	before = [volume.Detach]
	after = [filesystem.UnmountRoot]

	def run(self, info):
		info.volume.unmap()
