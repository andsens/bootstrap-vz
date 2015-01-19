from base import BasePartition


class PartitionGap(BasePartition):
	"""Represents a non-existent partition
	A gap in the partitionmap
	"""

	# The states for our state machine. It can neither be create nor mapped.
	events = []

	def __init__(self, size, previous):
		"""
		:param Bytes size: Size of the partition
		:param BasePartition previous: The partition that preceeds this one
		"""
		super(PartitionGap, self).__init__(size, None, None, previous)

	def get_index(self):
		"""Gets the index of this partition in the partition map
		Note that PartitionGap.get_index() simply returns the index of the
		previous partition, since a gap does not count towards
		the number of partitions.
		If there is no previous partition 0 will be returned
		(although partitions really are 1 indexed)

		:return: The index of the partition in the partition map
		:rtype: int
		"""
		if self.previous is None:
			return 0
		else:
			# Recursive call to the previous partition, walking up the chain...
			return self.previous.get_index()
