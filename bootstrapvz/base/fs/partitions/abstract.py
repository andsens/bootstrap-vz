from abc import ABCMeta
from abc import abstractmethod
import os.path
from bootstrapvz.common.tools import log_check_call
from bootstrapvz.common.fsm_proxy import FSMProxy


class AbstractPartition(FSMProxy):
	"""Abstract representation of a partiton
	This class is a finite state machine and represents the state of the real partition
	"""

	__metaclass__ = ABCMeta

	# Our states
	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'created'},
	          {'name': 'format', 'src': 'created', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          ]

	class Mount(object):
		"""Represents a mount into the partition
		"""
		def __init__(self, source, destination, opts):
			"""
			Args:
				source (str,AbstractPartition): The path from where we mount or a partition
				destination (str): The path of the mountpoint
				opts (list): List of options to pass to the mount command
			"""
			self.source      = source
			self.destination = destination
			self.opts        = opts

		def mount(self, prefix):
			"""Performs the mount operation or forwards it to another partition

			Args:
				prefix (str): Path prefix of the mountpoint
			"""
			mount_dir = os.path.join(prefix, self.destination)
			# If the source is another partition, we tell that partition to mount itself
			if isinstance(self.source, AbstractPartition):
				self.source.mount(destination=mount_dir)
			else:
				log_check_call(['mount'] + self.opts + [self.source, mount_dir])
			self.mount_dir = mount_dir

		def unmount(self):
			"""Performs the unmount operation or asks the partition to unmount itself
			"""
			# If its a partition, it can unmount itself
			if isinstance(self.source, AbstractPartition):
				self.source.unmount()
			else:
				log_check_call(['umount', self.mount_dir])
			del self.mount_dir

	def __init__(self, size, filesystem, format_command):
		"""
		Args:
			size (Bytes): Size of the partition
			filesystem (str): Filesystem the partition should be formatted with
			format_command (list): Optional format command, valid variables are fs, device_path and size
		"""
		self.size           = size
		self.filesystem     = filesystem
		self.format_command = format_command
		# Path to the partition
		self.device_path    = None
		# Dictionary with mount points as keys and Mount objects as values
		self.mounts         = {}

		# Create the configuration for our state machine
		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': {}}
		super(AbstractPartition, self).__init__(cfg)

	def get_uuid(self):
		"""Gets the UUID of the partition

		Returns:
			str. The UUID of the partition
		"""
		[uuid] = log_check_call(['blkid', '-s', 'UUID', '-o', 'value', self.device_path])
		return uuid

	@abstractmethod
	def get_start(self):
		pass

	def get_end(self):
		"""Gets the end of the partition

		Returns:
			Bytes. The end of the partition
		"""
		return self.get_start() + self.size

	def _before_format(self, e):
		"""Formats the partition
		"""
		# If there is no explicit format_command define we simply call mkfs.fstype
		if self.format_command is None:
			format_command = ['mkfs.{fs}', '{device_path}']
		else:
			format_command = self.format_command
		variables = {'fs': self.filesystem,
		             'device_path': self.device_path,
		             'size': self.size,
		             }
		command = map(lambda part: part.format(**variables), format_command)
		# Format the partition
		log_check_call(command)

	def _before_mount(self, e):
		"""Mount the partition
		"""
		log_check_call(['mount', '--types', self.filesystem, self.device_path, e.destination])
		self.mount_dir = e.destination

	def _after_mount(self, e):
		"""Mount any mounts associated with this partition
		"""
		# Make sure we mount in ascending order of mountpoint path length
		# This ensures that we don't mount /dev/pts before we mount /dev
		for destination in sorted(self.mounts.iterkeys(), key=len):
			self.mounts[destination].mount(self.mount_dir)

	def _before_unmount(self, e):
		"""Unmount any mounts associated with this partition
		"""
		# Unmount the mounts in descending order of mounpoint path length
		# You cannot unmount /dev before you have unmounted /dev/pts
		for destination in sorted(self.mounts.iterkeys(), key=len, reverse=True):
			self.mounts[destination].unmount()
		log_check_call(['umount', self.mount_dir])
		del self.mount_dir

	def add_mount(self, source, destination, opts=[]):
		"""Associate a mount with this partition
		Automatically mounts it

		Args:
			source (str,AbstractPartition): The source of the mount
			destination (str): The path to the mountpoint
			opts (list): Any options that should be passed to the mount command
		"""
		# Create a new mount object, mount it if the partition is mounted and put it in the mounts dict
		mount = self.Mount(source, destination, opts)
		if self.fsm.current == 'mounted':
			mount.mount(self.mount_dir)
		self.mounts[destination] = mount

	def remove_mount(self, destination):
		"""Remove a mount from this partition
		Automatically unmounts it

		Args:
			destination (str): The mountpoint path of the mount that should be removed
		"""
		# Unmount the mount if the partition is mounted and delete it from the mounts dict
		# If the mount is already unmounted and the source is a partition, this will raise an exception
		if self.fsm.current == 'mounted':
			self.mounts[destination].unmount()
		del self.mounts[destination]
