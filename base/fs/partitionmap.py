from common.tools import log_check_call
from partitions.partition import Partition
from partitions.swap import Swap
from exceptions import PartitionError


class PartitionMap(object):

	def __init__(self, data):
		self.boot = None
		self.swap = None
		self.mount_points = []
		if 'boot' in data:
			self.boot = Partition(data['boot']['size'], data['boot']['filesystem'], None)
			self.mount_points.append(('/boot', self.boot))
		self.root = Partition(data['root']['size'], data['root']['filesystem'], self.boot)
		self.mount_points.append(('/', self.root))
		if 'swap' in data:
			self.swap = Swap(data['swap']['size'], self.root)
			self.mount_points.append(('none', self.root))
		self.partitions = filter(lambda p: p is not None, [self.boot, self.root, self.swap])

	def get_total_size(self):
		return sum(p.size for p in self.partitions)

	def create(self, volume):
		log_check_call(['/sbin/parted', '--script', '--align', 'optimal', volume.device_path,
		                '--', 'mklabel', 'gpt'])
		for partition in self.partitions:
			partition.create(volume)

		boot_idx = self.root.get_index()
		if self.boot is not None:
			boot_idx = self.boot.get_index()
		log_check_call(['/sbin/parted', '--script', volume.device_path,
		                '--', 'set', str(boot_idx), 'bios_grub', 'on'])

	def map(self, volume):
		try:
			mappings = log_check_call(['/sbin/kpartx', '-l', volume.device_path])
			import re
			regexp = re.compile('^(?P<name>.+[^\d](?P<p_idx>\d+)) : '
			                    '(?P<start_blk>\d) (?P<num_blks>\d+) '
			                    '{device_path} (?P<blk_offset>\d+)$'
			                    .format(device_path=volume.device_path))
			log_check_call(['/sbin/kpartx', '-a', volume.device_path])
			import os.path
			for mapping in mappings:
				match = regexp.match(mapping)
				if match is None:
					raise PartitionError('Unable to parse kpartx output: {line}'.format(line=mapping))
				partition_path = os.path.join('/dev/mapper', match.group('name'))
				p_idx = int(match.group('p_idx'))-1
				self.partitions[p_idx].map(partition_path)

			for idx, partition in enumerate(self.partitions):
				if not partition.state() in ['mapped', 'formatted']:
					raise PartitionError('kpartx did not map partition #{idx}'.format(idx=idx+1))

		except PartitionError as e:
			for partition in self.partitions:
				if partition.state() in ['mapped', 'formatted']:
					partition.unmap()
			log_check_call(['/sbin/kpartx', '-d', volume.device_path])
			raise e

	def unmap(self, volume):
		for partition in self.partitions:
			partition.unmap()
		log_check_call(['/sbin/kpartx', '-d', volume.device_path])

	def format(self):
		for partition in self.partitions:
			partition.format()

	def mount_root(self, destination):
		self.root.mount(destination)

	def unmount_root(self):
		self.root.unmount()

	def mount_boot(self):
		import os.path
		destination = os.path.join(self.root.mount_dir, 'boot')
		self.boot.mount(destination)

	def unmount_boot(self):
		self.boot.unmount()
