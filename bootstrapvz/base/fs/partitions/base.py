from abstract import AbstractPartition


class BasePartition(AbstractPartition):
	"""Represents a partition that is actually a partition (and not a virtual one like 'Single')
	"""

	# Override the states of the abstract partition
	# A real partition can be mapped and unmapped
	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
	          {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
	          {'name': 'format', 'src': 'mapped', 'dst': 'formatted'},
	          {'name': 'mount', 'src': 'formatted', 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          {'name': 'unmap', 'src': 'formatted', 'dst': 'unmapped_fmt'},

	          {'name': 'map', 'src': 'unmapped_fmt', 'dst': 'formatted'},
	          {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
	          ]

	def __init__(self, size, filesystem, format_command, previous):
		"""
		Args:
			size (Bytes): Size of the partition
			filesystem (str): Filesystem the partition should be formatted with
			format_command (list): Optional format command, valid variables are fs, device_path and size
			previous (BasePartition): The partition that preceeds this one
		"""
		# By saving the previous partition we have
		# a linked list that partitions can go backwards in to find the first partition.
		self.previous = previous
		from common.bytes import Bytes
		# Initialize the offset to 0 bytes, may be changed later
		self.offset = Bytes(0)
		# List of flags that parted should put on the partition
		self.flags = []
		super(BasePartition, self).__init__(size, filesystem, format_command)

	def create(self, volume):
		"""Creates the partition

		Args:
			volume (Volume): The volume to create the partition on
		"""
		self.fsm.create(volume=volume)

	def get_index(self):
		"""Gets the index of this partition in the partition map

		Returns:
			int. The index of the partition in the partition map
		"""
		if self.previous is None:
			# Partitions are 1 indexed
			return 1
		else:
			# Recursive call to the previous partition, walking up the chain...
			return self.previous.get_index() + 1

	def get_start(self):
		"""Gets the starting byte of this partition

		Returns:
			Bytes. The starting byte of this partition
		"""
		if self.previous is None:
			# If there is no previous partition, this partition begins at the offset
			return self.offset
		else:
			# Get the end of the previous partition and add the offset of this partition
			return self.previous.get_end() + self.offset

	def map(self, device_path):
		"""Maps the partition to a device_path

		Args:
			device_path (str): The device patht his partition should be mapped to
		"""
		self.fsm.map(device_path=device_path)

	def _before_create(self, e):
		"""Creates the partition
		"""
		from common.tools import log_check_call
		# The create command is failry simple, start and end are just Bytes objects coerced into strings
		create_command = ('mkpart primary {start} {end}'
		                  .format(start=str(self.get_start()),
		                          end=str(self.get_end())))
		# Create the partition
		log_check_call(['parted', '--script', '--align', 'none', e.volume.device_path,
		                '--', create_command])

		# Set any flags on the partition
		for flag in self.flags:
			log_check_call(['parted', '--script', e.volume.device_path,
			                '--', ('set {idx} {flag} on'
			                       .format(idx=str(self.get_index()), flag=flag))])

	def _before_map(self, e):
		# Set the device path
		self.device_path = e.device_path

	def _before_unmap(self, e):
		# When unmapped, the device_path ifnromation becomes invalid, so we delete it
		self.device_path = None
