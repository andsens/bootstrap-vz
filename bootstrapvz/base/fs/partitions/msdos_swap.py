from bootstrapvz.common.tools import log_check_call
from msdos import MSDOSPartition


class MSDOSSwapPartition(MSDOSPartition):
    """Represents a MS-DOS swap partition
    """

    def __init__(self, size, previous):
        """
        :param Bytes size: Size of the partition
        :param BasePartition previous: The partition that preceeds this one
        """
        super(MSDOSSwapPartition, self).__init__(size, 'swap', None, previous)

    def _before_format(self, e):
        log_check_call(['mkswap', self.device_path])
