from abc import ABCMeta
from abc import abstractmethod
from common.tools import log_check_call
from common.fsm_proxy import FSMProxy


class AbstractPartition(FSMProxy):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'created'},
	          {'name': 'format', 'src': 'created', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          ]

	def __init__(self, size, filesystem):
		self.size          = size
		self.filesystem    = filesystem
		self.device_path   = None

		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': {}}
		super(AbstractPartition, self).__init__(cfg)

	def is_blocking(self):
		return self.is_state('mounted')

	def get_uuid(self):
		[uuid] = log_check_call(['/sbin/blkid', '-s', 'UUID', '-o', 'value', self.device_path])
		return uuid

	def create(self, volume):
		self.fsm.create(volume=volume)

	@abstractmethod
	def _before_create(self, e):
		pass

	def _before_format(self, e):
		mkfs = '/sbin/mkfs.{fs}'.format(fs=self.filesystem)
		log_check_call([mkfs, self.device_path])

	def mount(self, destination):
		self.fsm.mount(destination=destination)

	def _before_mount(self, e):
		log_check_call(['/bin/mount', '--types', self.filesystem, self.device_path, e.destination])
		self.mount_dir = e.destination

	def _before_unmount(self, e):
		log_check_call(['/bin/umount', self.mount_dir])
		del self.mount_dir
