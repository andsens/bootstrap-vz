from abstract import AbstractPartitionMap
from ..partitions.gpt import GPTPartition
from ..partitions.gpt_swap import GPTSwapPartition
from common.tools import log_check_call


class GPTPartitionMap(AbstractPartitionMap):

	def __init__(self, data, bootloader):
		self.partitions = []

		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None

		if bootloader == 'grub':
			from ..partitions.unformatted import UnformattedPartition
			self.grub_boot = UnformattedPartition(2, last_partition())
			self.grub_boot.flags.append('bios_grub')
			self.partitions.append(self.grub_boot)

		if 'boot' in data:
			self.boot = GPTPartition(data['boot']['size'], data['boot']['filesystem'], 'boot', last_partition())
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = GPTSwapPartition(data['swap']['size'], last_partition())
			self.partitions.append(self.swap)
		self.root = GPTPartition(data['root']['size'], data['root']['filesystem'], 'root', last_partition())
		self.partitions.append(self.root)

		# getattr(self, 'boot', self.root).flags.append('boot')
		if bootloader == 'extlinux':
			getattr(self, 'boot', self.root).flags.append('legacy_boot')

		super(GPTPartitionMap, self).__init__(bootloader)

	def _before_create(self, event):
		volume = event.volume
		log_check_call(['/sbin/parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'gpt'])
		for partition in self.partitions:
			partition.create(volume)
