from base.fs.volume import Volume
from common.tools import log_check_call
from base.fs.exceptions import VolumeError


# QEMU formats:
# raw, host_device, qcow2, qcow, cow, vdi, vmdk, vpc, cloop


class LoopbackVolume(Volume):

	link_dm_events = [{'name': 'link_dm_node', 'src': 'partitioned', 'dst': 'linked'},
	                  {'name': 'map', 'src': 'linked', 'dst': 'mapped_lnk'},
	                  {'name': 'format', 'src': 'mapped_lnk', 'dst': 'formatted_lnk'},
	                  {'name': 'mount', 'src': ['formatted_lnk', 'mounted_lnk'], 'dst': 'mounted_lnk'},
	                  {'name': 'unmount', 'src': 'mounted_lnk', 'dst': 'formatted_lnk'},
	                  {'name': 'unmap', 'src': 'formatted_lnk', 'dst': 'partitioned_fmt_lnk'},
	                  {'name': 'unlink_dm_node', 'src': 'partitioned_fmt_lnk', 'dst': 'partitioned_fmt'},

	                  {'name': 'link_dm_node', 'src': 'partitioned_fmt', 'dst': 'partitioned_fmt_lnk'},
	                  {'name': 'map', 'src': 'partitioned_fmt_lnk', 'dst': 'formatted_lnk'},
	                  {'name': 'unmap', 'src': 'mapped_lnk', 'dst': 'linked'},
	                  {'name': 'unlink_dm_node', 'src': 'linked', 'dst': 'partitioned'},
	                  ]

	extension = 'raw'

	def __init__(self, partition_map, callbacks={}):
		callbacks.update({'onbeforecreate': self._create,
		                  'onbeforeattach': self._attach,
		                  'onbeforedetach': self._detach,
		                  'onbeforedelete': self._delete,
		                  'onbeforelink_dm_node': self._link_dm_node,
		                  'onbeforeunlink_dm_node': self._unlink_dm_node,
		                  })
		self.events.extend(self.link_dm_events)
		super(LoopbackVolume, self).__init__(partition_map, callbacks=callbacks)

	def create(self, image_path):
		self.fsm.create(image_path=image_path)

	def _create(self, e):
		self.image_path = e.image_path
		log_check_call(['/usr/bin/qemu-img', 'create', '-f', 'raw', self.image_path, str(self.size) + 'M'])

	def _attach(self, e):
		[self.loop_device_path] = log_check_call(['/sbin/losetup', '--show', '--find', self.image_path])
		self.device_path = self.loop_device_path

	def _link_dm_node(self, e):
		import re
		loop_device_name = re.match('^/dev/(?P<name>.*)$', self.loop_device_path).group('name')
		from . import get_major_minor_dev_num
		major, minor = get_major_minor_dev_num(loop_device_name)
		sectors = self.size*1024*1024/512
		table = ('{log_start_sec} {sectors} linear {major}:{minor} {start_sec}'
		         .format(log_start_sec=0,
		                 sectors=sectors,
		                 major=major,
		                 minor=minor,
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

	def _unlink_dm_node(self, e):
		log_check_call(['/sbin/dmsetup', 'remove', self.dm_node_name])
		del self.dm_node_name
		del self.dm_node_path
		self.device_path = self.loop_device_path

	def _detach(self, e):
		log_check_call(['/sbin/losetup', '--detach', self.loop_device_path])
		del self.loop_device_path
		del self.device_path

	def _delete(self, e):
		from os import remove
		remove(self.image_path)
		del self.image_path
