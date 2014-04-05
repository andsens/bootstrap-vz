from abstract import AbstractPartition


class SinglePartition(AbstractPartition):
	"""Represents a single virtual partition on an unpartitioned volume
	"""

	def get_start(self):
		"""Gets the starting byte of this partition

		Returns:
			Bytes. The starting byte of this partition
		"""
		from bootstrapvz.common.bytes import Bytes
		# On an unpartitioned volume there is no offset and no previous partition
		return Bytes(0)
