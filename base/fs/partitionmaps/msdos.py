from abstract import AbstractPartitionMap
from ..partitions.msdos import MSDOSPartition
from ..partitions.msdos_swap import MSDOSSwapPartition
from common.tools import log_check_call


class MSDOSPartitionMap(AbstractPartitionMap):

	def __init__(self, data):
		self.partitions = []

		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None
		if 'boot' in data:
			self.boot = MSDOSPartition(data['boot']['size'], data['boot']['filesystem'], None)
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = MSDOSSwapPartition(data['swap']['size'], last_partition())
			self.partitions.append(self.swap)
		self.root = MSDOSPartition(data['root']['size'], data['root']['filesystem'], last_partition())
		self.partitions.append(self.root)

		super(MSDOSPartitionMap, self).__init__()

	def _before_create(self, event):
		volume = event.volume
		log_check_call(['/sbin/parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'msdos'])
		for partition in self.partitions:
			partition.create(volume)

		boot_idx = getattr(self, 'boot', self.root).get_index()
		log_check_call(['/sbin/parted', '--script', volume.device_path,
		                '--', 'set ' + str(boot_idx) + ' boot on'])
