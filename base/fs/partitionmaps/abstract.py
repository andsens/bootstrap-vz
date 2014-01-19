from abc import ABCMeta
from abc import abstractmethod
from common.tools import log_check_call
from common.fsm_proxy import FSMProxy
from ..exceptions import PartitionError


class AbstractPartitionMap(FSMProxy):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
	          {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
	          {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
	          ]

	def __init__(self, bootloader):
		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': {}}
		super(AbstractPartitionMap, self).__init__(cfg)

	def is_blocking(self):
		return self.fsm.current == 'mapped'

	def get_total_size(self):
		return self.partitions[-1].get_end()

	def create(self, volume):
		self.fsm.create(volume=volume)

	@abstractmethod
	def _before_create(self, event):
		pass

	def map(self, volume):
		self.fsm.map(volume=volume)

	def _before_map(self, event):
		volume = event.volume
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
				p_idx = int(match.group('p_idx')) - 1
				self.partitions[p_idx].map(partition_path)

			for idx, partition in enumerate(self.partitions):
				if partition.fsm.current not in ['mapped', 'formatted']:
					raise PartitionError('kpartx did not map partition #{idx}'.format(idx=idx + 1))

		except PartitionError as e:
			for partition in self.partitions:
				if not partition.fsm.can('unmap'):
					partition.unmap()
			log_check_call(['/sbin/kpartx', '-d', volume.device_path])
			raise e

	def unmap(self, volume):
		self.fsm.unmap(volume=volume)

	def _before_unmap(self, event):
		volume = event.volume
		for partition in self.partitions:
			if partition.fsm.cannot('unmap'):
				msg = 'The partition {partition} prevents the unmap procedure'.format(partition=partition)
				raise PartitionError(msg)
		log_check_call(['/sbin/kpartx', '-d', volume.device_path])
		for partition in self.partitions:
			partition.unmap()
