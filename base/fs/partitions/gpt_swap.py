from common.tools import log_check_call
from gpt import GPTPartition


class GPTSwapPartition(GPTPartition):

	def __init__(self, size, previous):
		super(GPTSwapPartition, self).__init__(size, 'swap', 'swap', previous)

	def _before_format(self, e):
		log_check_call(['/sbin/mkswap', self.device_path])
