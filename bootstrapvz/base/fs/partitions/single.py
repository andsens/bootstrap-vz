from abstract import AbstractPartition


class SinglePartition(AbstractPartition):
	"""Represents a single virtual partition on an unpartitioned volume
	"""

	def get_start(self):
		"""Gets the starting byte of this partition

		:return: The starting byte of this partition
		:rtype: Sectors
		"""
		from bootstrapvz.common.sectors import Sectors
		# On an unpartitioned volume there is no offset and no previous partition
		return Sectors(0, self.size.sector_size)
