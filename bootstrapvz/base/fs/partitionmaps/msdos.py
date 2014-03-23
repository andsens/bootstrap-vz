from abstract import AbstractPartitionMap
from ..partitions.msdos import MSDOSPartition
from ..partitions.msdos_swap import MSDOSSwapPartition
from bootstrapvz.common.tools import log_check_call


class MSDOSPartitionMap(AbstractPartitionMap):
	"""Represents a MS-DOS partition map
	Sometimes also called MBR (but that confuses the hell out of me, so ms-dos it is)
	"""

	def __init__(self, data, bootloader):
		"""
		Args:
			data (dict): volume.partitions part of the manifest
			bootloader (str): Name of the bootloader we will use for bootstrapping
		"""
		from bootstrapvz.common.bytes import Bytes
		# List of partitions
		self.partitions = []

		# Returns the last partition unless there is none
		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None

		# The boot and swap partitions are optional
		if 'boot' in data:
			self.boot = MSDOSPartition(Bytes(data['boot']['size']),
			                           data['boot']['filesystem'], data['boot'].get('format_command', None),
			                           last_partition())
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = MSDOSSwapPartition(Bytes(data['swap']['size']), last_partition())
			self.partitions.append(self.swap)
		self.root = MSDOSPartition(Bytes(data['root']['size']),
		                           data['root']['filesystem'], data['root'].get('format_command', None),
		                           last_partition())
		self.partitions.append(self.root)

		# Mark boot as the boot partition, or root, if boot does not exist
		getattr(self, 'boot', self.root).flags.append('boot')

		# If we are using the grub bootloader, we will need to create a 2 MB offset at the beginning
		# of the partitionmap and steal it from the first partition
		if bootloader == 'grub':
			self.partitions[0].offset = Bytes('2MiB')
			self.partitions[0].size -= self.partitions[0].offset

		super(MSDOSPartitionMap, self).__init__(bootloader)

	def _before_create(self, event):
		volume = event.volume
		# Disk alignment still plays a role in virtualized environment,
		# but I honestly have no clue as to what best practice is here, so we choose 'none'
		log_check_call(['parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'msdos'])
		# Create the partitions
		for partition in self.partitions:
			partition.create(volume)
