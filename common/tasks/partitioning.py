from base import Task
from common import phases
import filesystem
import volume


class PartitionVolume(Task):
	description = 'Partitioning the volume'
	phase = phases.volume_preparation

	@classmethod
	def run(cls, info):
		info.volume.partition_map.create(info.volume)


class MapPartitions(Task):
	description = 'Mapping volume partitions'
	phase = phases.volume_preparation
	predecessors = [PartitionVolume]
	successors = [filesystem.Format]

	@classmethod
	def run(cls, info):
		info.volume.partition_map.map(info.volume)


class UnmapPartitions(Task):
	description = 'Removing volume partitions mapping'
	phase = phases.volume_unmounting
	predecessors = [filesystem.UnmountRoot]
	successors = [volume.Detach]

	@classmethod
	def run(cls, info):
		info.volume.partition_map.unmap(info.volume)
