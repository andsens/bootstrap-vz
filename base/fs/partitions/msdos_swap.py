from common.tools import log_check_call
from msdos import MSDOSPartition


class MSDOSSwapPartition(MSDOSPartition):

	def __init__(self, size, previous):
		super(MSDOSSwapPartition, self).__init__(size, 'swap', previous)

	def _before_format(self, e):
		log_check_call(['/sbin/mkswap', self.device_path])
