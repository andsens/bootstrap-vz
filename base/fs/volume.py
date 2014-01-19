from abc import ABCMeta
from common.fsm_proxy import FSMProxy
from common.tools import log_check_call
from exceptions import VolumeError
from partitionmaps.none import NoPartitions


class Volume(FSMProxy):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'detached'},
	          {'name': 'attach', 'src': 'detached', 'dst': 'attached'},
	          {'name': 'link_dm_node', 'src': 'attached', 'dst': 'linked'},
	          {'name': 'unlink_dm_node', 'src': 'linked', 'dst': 'attached'},
	          {'name': 'detach', 'src': 'attached', 'dst': 'detached'},
	          {'name': 'delete', 'src': 'detached', 'dst': 'deleted'},
	          ]

	def __init__(self, partition_map):
		self.device_path = None
		self.real_device_path = None
		self.partition_map = partition_map
		self.size = self.partition_map.get_total_size()

		callbacks = {'onbeforedetach': self._check_blocking}
		if isinstance(self.partition_map, NoPartitions):
			def set_dev_path(e):
				self.partition_map.root.device_path = self.device_path
			callbacks['onafterattach'] = set_dev_path
			callbacks['onlink_dm_node'] = set_dev_path
			callbacks['onunlink_dm_node'] = set_dev_path

		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': callbacks}
		super(Volume, self).__init__(cfg)

	def _after_create(self, e):
		if isinstance(self.partition_map, NoPartitions):
			self.partition_map.root.create()

	def _check_blocking(self, e):
		if self.partition_map.is_blocking():
			raise VolumeError('The partitionmap prevents the detach procedure')

	def _before_link_dm_node(self, e):
		import os.path
		from common.fs import get_partitions
		proc_partitions = get_partitions()
		device_name = os.path.basename(self.device_path)
		device_partition = proc_partitions[device_name]

		# The sector the volume should start at in the new volume
		logical_start_sector = getattr(e, 'logical_start_sector', 0)

		# The offset at which the volume should begin to be mapped in the new volume
		start_sector = getattr(e, 'start_sector', 0)

		sectors = getattr(e, 'sectors', int(self.size / 512) - start_sector)

		table = ('{log_start_sec} {sectors} linear {major}:{minor} {start_sec}'
		         .format(log_start_sec=logical_start_sector,
		                 sectors=sectors,
		                 major=device_partition['major'],
		                 minor=device_partition['minor'],
		                 start_sec=start_sector))
		import string
		import os.path
		for letter in string.ascii_lowercase:
			dev_name = 'vd' + letter
			dev_path = os.path.join('/dev/mapper', dev_name)
			if not os.path.exists(dev_path):
				self.dm_node_name = dev_name
				self.dm_node_path = dev_path
				break

		if not hasattr(self, 'dm_node_name'):
			raise VolumeError('Unable to find a free block device path for mounting the bootstrap volume')

		log_check_call(['/sbin/dmsetup', 'create', self.dm_node_name], table)
		self.unlinked_device_path = self.device_path
		self.device_path = self.dm_node_path

	def _before_unlink_dm_node(self, e):
		log_check_call(['/sbin/dmsetup', 'remove', self.dm_node_name])
		del self.dm_node_name
		del self.dm_node_path
		self.device_path = self.unlinked_device_path
