from common.tools import log_check_call
from base import BasePartition


class GPTPartition(BasePartition):

	def __init__(self, size, filesystem, name, previous):
		self.name = name
		super(GPTPartition, self).__init__(size, filesystem, previous)

	def _before_create(self, e):
		super(GPTPartition, self)._before_create(e)
		# partition name only works for gpt, for msdos that becomes the part-type (primary, extended, logical)
		name_command = ('name {idx} {name}'
		                .format(idx=self.get_index(),
		                        name=self.name))
		log_check_call(['/sbin/parted', '--script', e.volume.device_path,
		                '--', name_command])
