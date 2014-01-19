from abstract import AbstractPartitionMap
from ..partitions.msdos import MSDOSPartition
from ..partitions.msdos_swap import MSDOSSwapPartition
from common.tools import log_check_call


class MSDOSPartitionMap(AbstractPartitionMap):

	def __init__(self, data, bootloader):
		from common.bytes import Bytes
		self.partitions = []

		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None

		if 'boot' in data:
			self.boot = MSDOSPartition(Bytes(data['boot']['size']), data['boot']['filesystem'], None)
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = MSDOSSwapPartition(Bytes(data['swap']['size']), last_partition())
			self.partitions.append(self.swap)
		self.root = MSDOSPartition(Bytes(data['root']['size']), data['root']['filesystem'], last_partition())
		self.partitions.append(self.root)

		getattr(self, 'boot', self.root).flags.append('boot')

		if bootloader == 'grub':
			self.partitions[0].offset = Bytes('2MiB')
			self.partitions[0].size -= self.partitions[0].offset

		super(MSDOSPartitionMap, self).__init__(bootloader)

	def _before_create(self, event):
		volume = event.volume
		log_check_call(['/sbin/parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'msdos'])
		for partition in self.partitions:
			partition.create(volume)
