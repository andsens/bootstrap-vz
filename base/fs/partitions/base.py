from abstract import AbstractPartition


class BasePartition(AbstractPartition):

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
	          {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
	          {'name': 'format', 'src': 'mapped', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          {'name': 'unmap', 'src': 'formatted', 'dst': 'unmapped_fmt'},

	          {'name': 'map', 'src': 'unmapped_fmt', 'dst': 'formatted'},
	          {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
	          ]

	def __init__(self, size, filesystem, previous):
		self.previous = previous
		super(BasePartition, self).__init__(size, filesystem)

	def create(self, volume):
		self.fsm.create(volume=volume)

	def get_index(self):
		if self.previous is None:
			return 1
		else:
			return self.previous.get_index()+1

	def get_start(self):
		if self.previous is None:
			return 0
		else:
			return self.previous.get_start() + self.previous.size

	def map(self, device_path):
		self.fsm.map(device_path=device_path)

	def _before_map(self, e):
		self.device_path = e.device_path

	def _before_unmap(self, e):
		self.device_path = None
