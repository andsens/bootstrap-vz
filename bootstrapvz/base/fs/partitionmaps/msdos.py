from abstract import AbstractPartitionMap
from ..partitions.msdos import MSDOSPartition
from ..partitions.msdos_swap import MSDOSSwapPartition
from bootstrapvz.common.tools import log_check_call


class MSDOSPartitionMap(AbstractPartitionMap):
    """Represents a MS-DOS partition map
    Sometimes also called MBR (but that confuses the hell out of me, so ms-dos it is)
    """

    def __init__(self, data, sector_size, bootloader):
        """
        :param dict data: volume.partitions part of the manifest
        :param int sector_size: Sectorsize of the volume
        :param str bootloader: Name of the bootloader we will use for bootstrapping
        """
        from bootstrapvz.common.sectors import Sectors

        # List of partitions
        self.partitions = []

        # Returns the last partition unless there is none
        def last_partition():
            return self.partitions[-1] if len(self.partitions) > 0 else None

        # The boot and swap partitions are optional
        if 'boot' in data:
            self.boot = MSDOSPartition(Sectors(data['boot']['size'], sector_size),
                                       data['boot']['filesystem'], data['boot'].get('format_command', None),
                                       last_partition())
            self.partitions.append(self.boot)

        # Offset all partitions by 1 sector.
        # parted in jessie has changed and no longer allows
        # partitions to be right next to each other.
        partition_gap = Sectors(1, sector_size)

        if 'swap' in data:
            self.swap = MSDOSSwapPartition(Sectors(data['swap']['size'], sector_size), last_partition())
            if self.swap.previous is not None:
                # No need to pad if this is the first partition
                self.swap.pad_start += partition_gap
                self.swap.size -= partition_gap
            self.partitions.append(self.swap)

        self.root = MSDOSPartition(Sectors(data['root']['size'], sector_size),
                                   data['root']['filesystem'], data['root'].get('format_command', None),
                                   last_partition())
        if self.root.previous is not None:
            self.root.pad_start += partition_gap
            self.root.size -= partition_gap
        self.partitions.append(self.root)

        # Mark boot as the boot partition, or root, if boot does not exist
        getattr(self, 'boot', self.root).flags.append('boot')

        # If we are using the grub bootloader, we will need to add a 2 MB offset
        # at the beginning of the partitionmap and steal it from the first partition.
        # The MBR offset is included in the grub offset, so if we don't use grub
        # we should reduce the size of the first partition and move it by only 512 bytes.
        if bootloader == 'grub':
            mbr_offset = Sectors('2MiB', sector_size)
        else:
            mbr_offset = Sectors('512B', sector_size)

        self.partitions[0].pad_start += mbr_offset
        self.partitions[0].size -= mbr_offset

        # Leave the last sector unformatted
        # parted in jessie thinks that a partition 10 sectors in size
        # goes from sector 0 to sector 9 (instead of 0 to 10)
        self.partitions[-1].pad_end += 1
        self.partitions[-1].size -= 1

        super(MSDOSPartitionMap, self).__init__(bootloader)

    def _before_create(self, event):
        volume = event.volume
        # Disk alignment still plays a role in virtualized environment,
        # but I honestly have no clue as to what best practice is here, so we choose 'none'
        log_check_call(['parted', '--script', '--align', 'none', volume.device_path,
                        '--', 'mklabel', 'msdos'])
        # Create the partitions
        for partition in self.partitions:
            partition.create(volume)
