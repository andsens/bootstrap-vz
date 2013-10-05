from ..partitions.single import SinglePartition


class NoPartitions(object):

	def __init__(self, data):
		root = data['root']
		self.root = SinglePartition(root['size'], root['filesystem'])
		self.partitions = [self.root]

	def is_blocking(self):
		return self.root.is_state('mounted')

	def get_total_size(self):
		return self.root.size
