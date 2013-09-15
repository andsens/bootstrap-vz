from common.tools import log_check_call
from partition import Partition


class Swap(Partition):

	def __init__(self, size, previous):
		super(Swap, self).__init__(size, 'swap', previous)

	def _format(self, e):
		log_check_call(['/sbin/mkswap', self.device_path])
