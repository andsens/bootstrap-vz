from abc import ABCMeta
from common.fsm_proxy import FSMProxy
from common.tools import log_check_call
from exceptions import VolumeError
from partitionmaps.none import NoPartitions


class Volume(FSMProxy):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'detached'},
	          {'name': 'attach', 'src': 'detached', 'dst': 'attached'},
	          {'name': 'detach', 'src': 'attached', 'dst': 'detached'},
	          {'name': 'delete', 'src': 'detached', 'dst': 'deleted'},
	          ]

	def __init__(self, partition_map):
		self.device_path = None
		self.partition_map = partition_map
		self.size = self.partition_map.get_total_size()

		callbacks = {'onbeforedetach': self._check_blocking}
		if isinstance(self.partition_map, NoPartitions):
			def set_dev_path(e):
				self.partition_map.root.device_path = self.device_path
			callbacks['onafterattach'] = set_dev_path

		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': callbacks}
		super(Volume, self).__init__(cfg)

	def _after_create(self, e):
		if isinstance(self.partition_map, NoPartitions):
			self.partition_map.root.create()

	def _check_blocking(self, e):
		if self.partition_map.is_blocking():
			raise VolumeError('The partitionmap prevents the detach procedure')
