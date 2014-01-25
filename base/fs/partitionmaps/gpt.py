from abstract import AbstractPartitionMap
from ..partitions.gpt import GPTPartition
from ..partitions.gpt_swap import GPTSwapPartition
from common.tools import log_check_call


class GPTPartitionMap(AbstractPartitionMap):

	def __init__(self, data, bootloader):
		from common.bytes import Bytes
		self.partitions = []

		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None

		gpt_offset = Bytes('17KiB')

		if bootloader == 'grub':
			from ..partitions.unformatted import UnformattedPartition
			self.grub_boot = UnformattedPartition(Bytes('1007KiB'), last_partition())
			self.grub_boot.offset = gpt_offset
			self.grub_boot.flags.append('bios_grub')
			self.partitions.append(self.grub_boot)

		if 'boot' in data:
			self.boot = GPTPartition(Bytes(data['boot']['size']), data['boot']['filesystem'],
			                         'boot', last_partition())
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = GPTSwapPartition(Bytes(data['swap']['size']), last_partition())
			self.partitions.append(self.swap)
		self.root = GPTPartition(Bytes(data['root']['size']), data['root']['filesystem'],
		                         'root', last_partition())
		self.partitions.append(self.root)

		if hasattr(self, 'grub_boot'):
			self.partitions[1].size -= gpt_offset
			self.partitions[1].size -= self.grub_boot.size
		else:
			self.partitions[0].offset = gpt_offset
			self.partitions[0].size -= gpt_offset

		super(GPTPartitionMap, self).__init__(bootloader)

	def _before_create(self, event):
		volume = event.volume
		log_check_call(['/sbin/parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'gpt'])
		for partition in self.partitions:
			partition.create(volume)
