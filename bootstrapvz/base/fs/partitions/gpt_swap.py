from bootstrapvz.common.tools import log_check_call
from gpt import GPTPartition


class GPTSwapPartition(GPTPartition):
    """Represents a GPT swap partition
    """

    def __init__(self, size, previous):
        """
        :param Bytes size: Size of the partition
        :param BasePartition previous: The partition that preceeds this one
        """
        super(GPTSwapPartition, self).__init__(size, 'swap', None, 'swap', previous)

    def _before_format(self, e):
        log_check_call(['mkswap', self.device_path])
