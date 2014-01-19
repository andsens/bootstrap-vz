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
		from common.bytes import Bytes
		self.offset = Bytes(0)
		self.flags = []
		super(BasePartition, self).__init__(size, filesystem)

	def create(self, volume):
		self.fsm.create(volume=volume)

	def get_index(self):
		if self.previous is None:
			return 1
		else:
			return self.previous.get_index() + 1

	def get_start(self):
		if self.previous is None:
			return self.offset
		else:
			return self.previous.get_end() + self.offset

	def map(self, device_path):
		self.fsm.map(device_path=device_path)

	def _before_create(self, e):
		from common.tools import log_check_call
		create_command = ('mkpart primary {start} {end}'
		                  .format(start=str(self.get_start()),
		                          end=str(self.get_end())))
		log_check_call(['/sbin/parted', '--script', '--align', 'none', e.volume.device_path,
		                '--', create_command])

		for flag in self.flags:
			log_check_call(['/sbin/parted', '--script', e.volume.device_path,
			                '--', ('set {idx} {flag} on'
			                       .format(idx=str(self.get_index()), flag=flag))])

	def _before_map(self, e):
		self.device_path = e.device_path

	def _before_unmap(self, e):
		self.device_path = None
