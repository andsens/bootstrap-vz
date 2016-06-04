import os
from abstract import AbstractPartition
from bootstrapvz.common.sectors import Sectors


class BasePartition(AbstractPartition):
    """Represents a partition that is actually a partition (and not a virtual one like 'Single')
    """

    # Override the states of the abstract partition
    # A real partition can be mapped and unmapped
    events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
              {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
              {'name': 'format', 'src': 'mapped', 'dst': 'formatted'},
              {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
              {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
              {'name': 'unmap', 'src': 'formatted', 'dst': 'unmapped_fmt'},

              {'name': 'map', 'src': 'unmapped_fmt', 'dst': 'formatted'},
              {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
              ]

    def __init__(self, size, filesystem, format_command, previous):
        """
        :param Bytes size: Size of the partition
        :param str filesystem: Filesystem the partition should be formatted with
        :param list format_command: Optional format command, valid variables are fs, device_path and size
        :param BasePartition previous: The partition that preceeds this one
        """
        # By saving the previous partition we have a linked list
        # that partitions can go backwards in to find the first partition.
        self.previous = previous
        # List of flags that parted should put on the partition
        self.flags = []
        # Path to symlink in /dev/disk/by-uuid (manually maintained by this class)
        self.disk_by_uuid_path = None
        super(BasePartition, self).__init__(size, filesystem, format_command)

    def create(self, volume):
        """Creates the partition

        :param Volume volume: The volume to create the partition on
        """
        self.fsm.create(volume=volume)

    def get_index(self):
        """Gets the index of this partition in the partition map

        :return: The index of the partition in the partition map
        :rtype: int
        """
        if self.previous is None:
            # Partitions are 1 indexed
            return 1
        else:
            # Recursive call to the previous partition, walking up the chain...
            return self.previous.get_index() + 1

    def get_start(self):
        """Gets the starting byte of this partition

        :return: The starting byte of this partition
        :rtype: Sectors
        """
        if self.previous is None:
            return Sectors(0, self.size.sector_size)
        else:
            return self.previous.get_end()

    def map(self, device_path):
        """Maps the partition to a device_path

        :param str device_path: The device path this partition should be mapped to
        """
        self.fsm.map(device_path=device_path)

    def link_uuid(self):
        # /lib/udev/rules.d/60-kpartx.rules does not create symlinks in /dev/disk/by-{uuid,label}
        # This patch would fix that: http://www.redhat.com/archives/dm-devel/2013-July/msg00080.html
        # For now we just do the uuid part ourselves.
        # This is mainly to fix a problem in update-grub where /etc/grub.d/10_linux
        # checks if the $GRUB_DEVICE_UUID exists in /dev/disk/by-uuid and falls
        # back to $GRUB_DEVICE if it doesn't.
        # $GRUB_DEVICE is /dev/mapper/xvd{f,g...}# (on ec2), opposed to /dev/xvda# when booting.
        # Creating the symlink ensures that grub consistently uses
        # $GRUB_DEVICE_UUID when creating /boot/grub/grub.cfg
        self.disk_by_uuid_path = os.path.join('/dev/disk/by-uuid', self.get_uuid())
        if not os.path.exists(self.disk_by_uuid_path):
            os.symlink(self.device_path, self.disk_by_uuid_path)

    def unlink_uuid(self):
        if os.path.isfile(self.disk_by_uuid_path):
            os.remove(self.disk_by_uuid_path)
        self.disk_by_uuid_path = None

    def _before_create(self, e):
        """Creates the partition
        """
        from bootstrapvz.common.tools import log_check_call
        # The create command is fairly simple:
        # - fs_type is the partition filesystem, as defined by parted:
        #   fs-type can be one of "fat16", "fat32", "ext2", "HFS", "linux-swap",
        #   "NTFS", "reiserfs", or "ufs".
        # - start and end are just Bytes objects coerced into strings
        if self.filesystem == 'swap':
            fs_type = 'linux-swap'
        else:
            fs_type = 'ext2'
        create_command = ('mkpart primary {fs_type} {start} {end}'
                          .format(fs_type=fs_type,
                                  start=str(self.get_start() + self.pad_start),
                                  end=str(self.get_end() - self.pad_end)))
        # Create the partition
        log_check_call(['parted', '--script', '--align', 'none', e.volume.device_path,
                        '--', create_command])

        # Set any flags on the partition
        for flag in self.flags:
            log_check_call(['parted', '--script', e.volume.device_path,
                            '--', ('set {idx} {flag} on'
                                   .format(idx=str(self.get_index()), flag=flag))])

    def _before_map(self, e):
        # Set the device path
        self.device_path = e.device_path
        if e.src == 'unmapped_fmt':
            # Only link the uuid if the partition is formatted
            self.link_uuid()

    def _after_format(self, e):
        # We do this after formatting because there otherwise would be no UUID
        self.link_uuid()

    def _before_unmap(self, e):
        # When unmapped, the device_path information becomes invalid, so we delete it
        self.device_path = None
        if e.src == 'formatted':
            self.unlink_uuid()
