from common.tools import log_check_call
from base import BasePartition


class MBRPartition(BasePartition):

	def _before_create(self, e):
		start = self.get_start()
		parted_command = ('mkpart primary {start}MiB {end}MiB'
		                  .format(start=str(start),
		                          end=str(start + self.size)))
		log_check_call(['/sbin/parted', '--script', '--align', 'none', e.volume.device_path,
		                '--', parted_command])
