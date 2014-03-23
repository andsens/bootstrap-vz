from ....common.tools import log_check_call
from base import BasePartition


class GPTPartition(BasePartition):
	"""Represents a GPT partition
	"""

	def __init__(self, size, filesystem, format_command, name, previous):
		"""
		Args:
			size (Bytes): Size of the partition
			filesystem (str): Filesystem the partition should be formatted with
			format_command (list): Optional format command, valid variables are fs, device_path and size
			name (str): The name of the partition
			previous (BasePartition): The partition that preceeds this one
		"""
		self.name = name
		super(GPTPartition, self).__init__(size, filesystem, format_command, previous)

	def _before_create(self, e):
		# Create the partition and then set the name of the partition afterwards
		super(GPTPartition, self)._before_create(e)
		# partition name only works for gpt, for msdos that becomes the part-type (primary, extended, logical)
		name_command = ('name {idx} {name}'
		                .format(idx=self.get_index(),
		                        name=self.name))
		log_check_call(['parted', '--script', e.volume.device_path,
		                '--', name_command])
