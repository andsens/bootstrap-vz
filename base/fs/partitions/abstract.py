from abc import ABCMeta
from abc import abstractmethod
import os.path
from common.tools import log_check_call
from common.fsm_proxy import FSMProxy


class AbstractPartition(FSMProxy):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'created'},
	          {'name': 'format', 'src': 'created', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          ]

	class Mount(object):
		def __init__(self, source, destination, opts):
			self.source      = source
			self.destination = destination
			self.opts        = opts

		def mount(self, prefix):
			mount_dir = os.path.join(prefix, self.destination)
			if isinstance(self.source, AbstractPartition):
				self.source.mount(destination=mount_dir)
			else:
				log_check_call(['mount'] + self.opts + [self.source, mount_dir])
			self.mount_dir = mount_dir

		def unmount(self):
			if isinstance(self.source, AbstractPartition):
				self.source.unmount()
			else:
				log_check_call(['umount', self.mount_dir])
			del self.mount_dir

	def __init__(self, size, filesystem, format_command):
		self.size           = size
		self.filesystem     = filesystem
		self.format_command = format_command
		self.device_path    = None
		self.mounts         = {}

		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': {}}
		super(AbstractPartition, self).__init__(cfg)

	def get_uuid(self):
		[uuid] = log_check_call(['blkid', '-s', 'UUID', '-o', 'value', self.device_path])
		return uuid

	@abstractmethod
	def get_start(self):
		pass

	def get_end(self):
		return self.get_start() + self.size

	def _before_format(self, e):
		if self.format_command is None:
			format_command = ['mkfs.{fs}', '{device_path}']
		else:
			format_command = self.format_command
		variables = {'fs': self.filesystem,
		             'device_path': self.device_path,
		             'size': self.size,
		             }
		command = map(lambda part: part.format(**variables), format_command)
		log_check_call(command)

	def _before_mount(self, e):
		log_check_call(['mount', '--types', self.filesystem, self.device_path, e.destination])
		self.mount_dir = e.destination

	def _after_mount(self, e):
		for destination in sorted(self.mounts.iterkeys(), key=len):
			self.mounts[destination].mount(self.mount_dir)

	def _before_unmount(self, e):
		for destination in sorted(self.mounts.iterkeys(), key=len, reverse=True):
			self.mounts[destination].unmount()
		log_check_call(['umount', self.mount_dir])
		del self.mount_dir

	def add_mount(self, source, destination, opts=[]):
		mount = self.Mount(source, destination, opts)
		if self.fsm.current == 'mounted':
			mount.mount(self.mount_dir)
		self.mounts[destination] = mount

	def remove_mount(self, destination):
		if self.fsm.current == 'mounted':
			self.mounts[destination].unmount()
		del self.mounts[destination]
