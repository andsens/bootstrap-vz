from bootstrapvz.base import Task
from bootstrapvz.common import phases
import filesystem
import host
import volume


class AddRequiredCommands(Task):
    description = 'Adding commands required for partitioning the volume'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        from bootstrapvz.base.fs.partitionmaps.none import NoPartitions
        if not isinstance(info.volume.partition_map, NoPartitions):
            info.host_dependencies['parted'] = 'parted'
            info.host_dependencies['kpartx'] = 'kpartx'


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
