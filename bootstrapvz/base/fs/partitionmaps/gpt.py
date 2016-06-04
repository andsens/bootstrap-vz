from abstract import AbstractPartitionMap
from ..partitions.gpt import GPTPartition
from ..partitions.gpt_swap import GPTSwapPartition
from bootstrapvz.common.tools import log_check_call


class GPTPartitionMap(AbstractPartitionMap):
    """Represents a GPT partition map
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

        if bootloader == 'grub':
            # If we are using the grub bootloader we need to create an unformatted partition
            # at the beginning of the map. Its size is 1007kb, which seems to be chosen so that
            # primary gpt + grub = 1024KiB
            # The 1 MiB will be subtracted later on, once we know what the subsequent partition is
            from ..partitions.unformatted import UnformattedPartition
            self.grub_boot = UnformattedPartition(Sectors('1MiB', sector_size), last_partition())
            self.partitions.append(self.grub_boot)

        # Offset all partitions by 1 sector.
        # parted in jessie has changed and no longer allows
        # partitions to be right next to each other.
        partition_gap = Sectors(1, sector_size)

        # The boot and swap partitions are optional
        if 'boot' in data:
            self.boot = GPTPartition(Sectors(data['boot']['size'], sector_size),
                                     data['boot']['filesystem'], data['boot'].get('format_command', None),
                                     'boot', last_partition())
            if self.boot.previous is not None:
                # No need to pad if this is the first partition
                self.boot.pad_start += partition_gap
                self.boot.size -= partition_gap
            self.partitions.append(self.boot)

        if 'swap' in data:
            self.swap = GPTSwapPartition(Sectors(data['swap']['size'], sector_size), last_partition())
            if self.swap.previous is not None:
                self.swap.pad_start += partition_gap
                self.swap.size -= partition_gap
            self.partitions.append(self.swap)

        self.root = GPTPartition(Sectors(data['root']['size'], sector_size),
                                 data['root']['filesystem'], data['root'].get('format_command', None),
                                 'root', last_partition())
        if self.root.previous is not None:
            self.root.pad_start += partition_gap
            self.root.size -= partition_gap
        self.partitions.append(self.root)

        if hasattr(self, 'grub_boot'):
            # Mark the grub partition as a bios_grub partition
            self.grub_boot.flags.append('bios_grub')
            # Subtract the grub partition size from the subsequent partition
            self.partitions[1].size -= self.grub_boot.size
        else:
            # Not using grub, mark the boot partition or root as bootable
            getattr(self, 'boot', self.root).flags.append('legacy_boot')

        # The first and last 34 sectors are reserved for the primary/secondary GPT
        primary_gpt_size = Sectors(34, sector_size)
        self.partitions[0].pad_start += primary_gpt_size
        self.partitions[0].size -= primary_gpt_size

        secondary_gpt_size = Sectors(34, sector_size)
        self.partitions[-1].pad_end += secondary_gpt_size
        self.partitions[-1].size -= secondary_gpt_size

        super(GPTPartitionMap, self).__init__(bootloader)

    def _before_create(self, event):
        """Creates the partition map
        """
        volume = event.volume
        # Disk alignment still plays a role in virtualized environment,
        # but I honestly have no clue as to what best practice is here, so we choose 'none'
        log_check_call(['parted', '--script', '--align', 'none', volume.device_path,
                        '--', 'mklabel', 'gpt'])
        # Create the partitions
        for partition in self.partitions:
            partition.create(volume)
