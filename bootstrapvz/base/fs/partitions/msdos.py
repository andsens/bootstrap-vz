from .base import BasePartition


class MSDOSPartition(BasePartition):
    """Represents an MS-DOS partition
    """
    def __init__(self, size, filesystem, format_command, mountopts, name, previous):
        """
        :param Bytes size: Size of the partition
        :param str filesystem: Filesystem the partition should be formatted with
        :param list format_command: Optional format command, valid variables are fs, device_path and size
        :param str name: The name of the partition
        :param BasePartition previous: The partition that preceeds this one
        """
        self.name = name
        super(MSDOSPartition, self).__init__(size, filesystem, format_command, mountopts, previous)
