from abstractpartition import AbstractPartition


class SinglePartition(AbstractPartition):

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'created'},
	          {'name': 'format', 'src': 'created', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          ]

	def __init__(self, size, filesystem, callbacks={}):
		callbacks['oncreate'] = self._create
		super(SinglePartition, self).__init__(size, filesystem, callbacks=callbacks)

	def create(self, volume):
		self.fsm.create(volume=volume)

	def _create(self, e):
		self.device_path = e.volume.device_path
