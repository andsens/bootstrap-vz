from common.tools import log_check_call
from base import BasePartition


class GPTPartition(BasePartition):

	def __init__(self, size, filesystem, name, previous):
		self.name = name
		super(GPTPartition, self).__init__(size, filesystem, previous)

	def _before_create(self, e):
		start = self.get_start()
		create_command = ('mkpart primary {start}MiB {end}MiB'
		                  .format(start=str(start),
		                          end=str(start + self.size)))
		log_check_call(['/sbin/parted', '--script', '--align', 'none', e.volume.device_path,
		                '--', create_command])

		# partition name only works for gpt, for msdos that becomes the part-type (primary, extended, logical)
		name_command = ('name {idx} {name}'
		                .format(idx=self.get_index(),
		                        name=self.name))
		log_check_call(['/sbin/parted', '--script', '--align', 'none', e.volume.device_path,
		                '--', name_command])
