from abstract import AbstractPartitionMap
from ..partitions.mbr import MBRPartition
from ..partitions.mbr_swap import MBRSwapPartition
from common.tools import log_check_call


class MBRPartitionMap(AbstractPartitionMap):

	def __init__(self, data):
		self.partitions = []

		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None
		if 'boot' in data:
			self.boot = MBRPartition(data['boot']['size'], data['boot']['filesystem'], None)
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = MBRSwapPartition(data['swap']['size'], last_partition())
			self.partitions.append(self.swap)
		self.root = MBRPartition(data['root']['size'], data['root']['filesystem'], last_partition())
		self.partitions.append(self.root)

		super(MBRPartitionMap, self).__init__()

	def get_total_size(self):
		return sum(p.size for p in self.partitions) + 1  # Post-MBR gap for embedding grub

	def _before_create(self, event):
		volume = event.volume
		log_check_call(['/sbin/parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'msdos'])
		for partition in self.partitions:
			partition.create(volume)

		boot_idx = self.root.get_index()
		if hasattr(self, 'boot'):
			boot_idx = self.boot.get_index()
		log_check_call(['/sbin/parted', '--script', volume.device_path,
		                '--', 'set ' + str(boot_idx) + ' boot on'])
