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
