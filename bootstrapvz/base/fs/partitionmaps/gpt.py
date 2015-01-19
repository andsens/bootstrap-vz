from abstract import AbstractPartitionMap
from ..partitions.gpt import GPTPartition
from ..partitions.gpt_swap import GPTSwapPartition
from ..partitions.gap import PartitionGap
from bootstrapvz.common.tools import log_check_call


class GPTPartitionMap(AbstractPartitionMap):
	"""Represents a GPT partition map
	"""

	def __init__(self, data, sector_size, bootloader):
		"""
		:param dict data: volume.partitions part of the manifest
		:param int sector_size: Sectorsize of the volume
		:param str bootloader: Name of the bootloader we will use for bootstrapping
		"""
		from bootstrapvz.common.sectors import Sectors

		# List of partitions
		self.partitions = []

		# Returns the last partition unless there is none
		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None

		# The first 34 sectors are reserved for the primary GPT
		primary_gpt = PartitionGap(Sectors(34, sector_size), last_partition())
		self.partitions.append(primary_gpt)

		if bootloader == 'grub':
			# If we are using the grub bootloader we need to create an unformatted partition
			# at the beginning of the map. Its size is 1007kb, which seems to be chosen so that
			# gpt_primary + grub = 1024KiB
			# So lets just specify grub size as 1MiB - 34 sectors
			from ..partitions.unformatted import UnformattedPartition
			grub_size = Sectors('1MiB', sector_size) - primary_gpt.size
			self.grub_boot = UnformattedPartition(grub_size, last_partition())
			# Mark the partition as a bios_grub partition
			self.grub_boot.flags.append('bios_grub')
			self.partitions.append(self.grub_boot)

		# The boot and swap partitions are optional
		if 'boot' in data:
			self.boot = GPTPartition(Sectors(data['boot']['size'], sector_size),
			                         data['boot']['filesystem'], data['boot'].get('format_command', None),
			                         'boot', last_partition())
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = GPTSwapPartition(Sectors(data['swap']['size'], sector_size), last_partition())
			self.partitions.append(self.swap)
		self.root = GPTPartition(Sectors(data['root']['size'], sector_size),
		                         data['root']['filesystem'], data['root'].get('format_command', None),
		                         'root', last_partition())
		self.partitions.append(self.root)

		# The last 34 sectors are reserved for the secondary GPT
		secondary_gpt = PartitionGap(Sectors(34, sector_size), last_partition())
		self.partitions.append(secondary_gpt)

		# reduce the size of the root partition so that the overall volume size is not exceeded
		self.root.size -= primary_gpt.size + secondary_gpt.size
		if hasattr(self, 'grub_boot'):
			self.root.size -= self.grub_boot.size

		super(GPTPartitionMap, self).__init__(bootloader)

	def _before_create(self, event):
		"""Creates the partition map
		"""
		volume = event.volume
		# Disk alignment still plays a role in virtualized environment,
		# but I honestly have no clue as to what best practice is here, so we choose 'none'
		log_check_call(['parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'gpt'])
		# Create the partitions
		for partition in self.partitions:
			if isinstance(partition, PartitionGap):
				continue
			partition.create(volume)
