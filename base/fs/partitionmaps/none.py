from ..partitions.single import SinglePartition


class NoPartitions(object):

	def __init__(self, data, bootloader):
		from common.bytes import Bytes
		self.root = SinglePartition(Bytes(data['root']['size']), data['root']['filesystem'])
		self.partitions = [self.root]

	def is_blocking(self):
		return self.root.fsm.current == 'mounted'

	def get_total_size(self):
		return self.root.get_end()
