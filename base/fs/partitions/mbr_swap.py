from common.tools import log_check_call
from mbr import MBRPartition


class MBRSwapPartition(MBRPartition):

	def __init__(self, size, previous):
		super(MBRSwapPartition, self).__init__(size, 'swap', previous)

	def _format(self, e):
		log_check_call(['/sbin/mkswap', self.device_path])
