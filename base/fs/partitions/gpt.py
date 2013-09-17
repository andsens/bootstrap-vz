from common.tools import log_check_call
from base import BasePartition


class GPTPartition(BasePartition):

	def __init__(self, size, filesystem, name, previous, callbacks={}):
		self.name = name
		super(GPTPartition, self).__init__(size, filesystem, previous, callbacks=callbacks)

	def _create(self, e):
		start = self.get_start()
		# {name} only works for gpt, for msdos that becomes the part-type (primary, extended, logical)
		parted_command = ('mkpart primary {start}MiB {end}MiB'
		                  .format(name=self.name,
		                          start=str(start),
		                          end=str(start + self.size)))
		log_check_call(['/sbin/parted', '--script', '--align', 'none', e.volume.device_path,
		                '--', parted_command])
