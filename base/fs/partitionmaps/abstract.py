from abc import ABCMeta
from abc import abstractmethod
from common.tools import log_check_call
from ..exceptions import PartitionError


class AbstractPartitionMap(object):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, data):
		pass

	def get_total_size(self):
		return sum(p.size for p in self.partitions) + 1

	@abstractmethod
	def create(self, volume):
		pass

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
