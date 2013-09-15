from common.tools import log_check_call
from abc import ABCMeta
from fysom import Fysom


class AbstractPartition(object):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'created'},
	          {'name': 'format', 'src': 'created', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          ]

	def __init__(self, size, filesystem, callbacks={}):
		self.size          = size
		self.filesystem    = filesystem
		self.device_path   = None
		self.initial_state = 'nonexistent'

		callbacks.update({'onbeforeformat': self._format,
		                  'onbeforemount': self._mount,
		                  'onbeforeunmount': self._unmount,
		                  })

		self.fsm = Fysom({'initial': 'nonexistent',
		                  'events': self.events,
		                  'callbacks': callbacks})
		from common.fsm import attach_proxy_methods
		attach_proxy_methods(self, self.events, self.fsm)

	def state(self):
		return self.fsm.current

	def force_state(self, state):
		self.fsm.current = state

	def get_uuid(self):
		[uuid] = log_check_call(['/sbin/blkid', '-s', 'UUID', '-o', 'value', self.device_path])
		return uuid

	def _format(self, e):
		mkfs = '/sbin/mkfs.{fs}'.format(fs=self.filesystem)
		log_check_call([mkfs, self.device_path])

	def mount(self, destination):
		self.fsm.mount(destination=destination)

	def _mount(self, e):
		log_check_call(['/bin/mount', '--types', self.filesystem, self.device_path, e.destination])
		self.mount_dir = e.destination

	def _unmount(self, e):
		log_check_call(['/bin/umount', self.mount_dir])
		del self.mount_dir
