from base.fs.volume import Volume
from common.tools import log_check_call
from base.fs.exceptions import VolumeError


# QEMU formats:
# raw, host_device, qcow2, qcow, cow, vdi, vmdk, vpc, cloop


class LoopbackVolume(Volume):

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'detached'},
	          {'name': 'attach', 'src': 'detached', 'dst': 'attached'},
	          {'name': 'link_dm_node', 'src': 'attached', 'dst': 'linked'},
            {'name': 'unlink_dm_node', 'src': 'linked', 'dst': 'attached'},
	          {'name': 'detach', 'src': 'attached', 'dst': 'detached'},
	          {'name': 'delete', 'src': 'detached', 'dst': 'deleted'},
	          ]

	extension = 'raw'

	def __init__(self, partition_map):
		super(LoopbackVolume, self).__init__(partition_map)

	def create(self, image_path):
		self.fsm.create(image_path=image_path)

	def _before_create(self, e):
		self.image_path = e.image_path
		log_check_call(['/usr/bin/qemu-img', 'create', '-f', 'raw', self.image_path, str(self.size) + 'M'])

	def _before_attach(self, e):
		[self.loop_device_path] = log_check_call(['/sbin/losetup', '--show', '--find', self.image_path])
		self.device_path = self.loop_device_path

	def _before_link_dm_node(self, e):
		import os.path
		from . import get_partitions
		proc_partitions = get_partitions()
		loop_device_name = os.path.basename(self.loop_device_path)
		loop_device_partition = proc_partitions[loop_device_name]

		sectors = self.size*1024*1024/512
		table = ('{log_start_sec} {sectors} linear {major}:{minor} {start_sec}'
		         .format(log_start_sec=0,
		                 sectors=sectors,
		                 major=loop_device_partition['major'],
		                 minor=loop_device_partition['minor'],
		                 start_sec=0))
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
		self.device_path = self.dm_node_path

	def _before_unlink_dm_node(self, e):
		log_check_call(['/sbin/dmsetup', 'remove', self.dm_node_name])
		del self.dm_node_name
		del self.dm_node_path
		self.device_path = self.loop_device_path

	def _before_detach(self, e):
		log_check_call(['/sbin/losetup', '--detach', self.loop_device_path])
		del self.loop_device_path
		del self.device_path

	def _before_delete(self, e):
		from os import remove
		remove(self.image_path)
		del self.image_path
