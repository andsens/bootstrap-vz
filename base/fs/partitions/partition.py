from common.tools import log_check_call
from abstractpartition import AbstractPartition


class Partition(AbstractPartition):

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
	          {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
	          {'name': 'map', 'src': 'unmapped_fmt', 'dst': 'formatted'},
	          {'name': 'format', 'src': 'mapped', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          {'name': 'unmap', 'src': 'formatted', 'dst': 'unmapped_fmt'},
	          {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
	          ]

	def __init__(self, size, filesystem, previous, callbacks={}):
		self.previous = previous
		callbacks.update({'onbeforecreate': self._create,
		                  'onbeforemap': self._map,
		                  'onbeforeunmap': self._unmap,
		                  })
		super(Partition, self).__init__(size, filesystem, callbacks=callbacks)

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

	def create(self, volume):
		self.fsm.create(volume=volume)

	def _create(self, e):
		start = self.get_start()
		# maybe use `parted -- name` to set partition name
		log_check_call(['/sbin/parted', '--script', '--align', 'optimal', e.volume.device_path,
		                '--', 'mkpart', 'primary', str(start), str(start + self.size)])

	def map(self, device_path):
		self.fsm.map(device_path=device_path)

	def _map(self, e):
		self.device_path = e.device_path

	def _unmap(self, e):
		self.device_path = None

# Partition flags:
# boot, root, swap, hidden, raid, lvm, lba, legacy_boot, palo


# Partition tables
# bsd, dvh, gpt, loop, mac, msdos, pc98, sun
