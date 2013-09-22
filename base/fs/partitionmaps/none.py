from ..partitions.single import SinglePartition
from common.fsm_proxy import FSMProxy


class NoPartitions(FSMProxy):

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'created'}]

	def __init__(self, data):
		root = data['root']
		self.root = SinglePartition(root['size'], root['filesystem'])
		self.partitions = [self.root]
		self.mount_points = [('/', self.root)]

		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': {}}
		super(NoPartitions, self).__init__(cfg)

	def is_blocking(self):
		return self.root.is_blocking()

	def get_total_size(self):
		return self.root.size

	def create(self, volume):
		self.fsm.create(volume=volume)

	def _before_create(self, event):
		self.root.create(event.volume)
