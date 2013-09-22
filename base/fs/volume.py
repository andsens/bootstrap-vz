from abc import ABCMeta
from common.fsm_proxy import FSMProxy
from common.tools import log_check_call
from exceptions import VolumeError


class Volume(FSMProxy):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'detached'},
	          {'name': 'attach', 'src': 'detached', 'dst': 'attached'},
	          {'name': 'mount_specials', 'src': 'attached', 'dst': 'specials_mounted'},
	          {'name': 'unmount_specials', 'src': 'specials_mounted', 'dst': 'attached'},
	          {'name': 'detach', 'src': 'attached', 'dst': 'detached'},
	          {'name': 'delete', 'src': 'detached', 'dst': 'deleted'},
	          ]

	def __init__(self, partition_map):
		self.device_path = None
		self.partition_map = partition_map
		self.size = self.partition_map.get_total_size()

		callbacks = {'onbeforedetach': self._check_blocking}
		from partitionmaps.none import NoPartitions
		if isinstance(self.partition_map, NoPartitions):
			callbacks['onafterattach'] = lambda e: self.partition_map.create(self)

		cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': callbacks}
		super(Volume, self).__init__(cfg)

	def _before_mount_specials(self, e):
		root = self.partition_map.root.mount_dir
		log_check_call(['/bin/mount', '--bind', '/dev', '{root}/dev'.format(root=root)])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'proc', 'none', '/proc'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'sysfs', 'none', '/sys'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'devpts', 'none', '/dev/pts'])

	def _before_unmount_specials(self, e):
		root = self.partition_map.root.mount_dir
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/dev/pts'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/sys'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/proc'])
		log_check_call(['/bin/umount', '{root}/dev'.format(root=root)])

	def _check_blocking(self, e):
		if self.partition_map.is_blocking():
			raise VolumeError('The partitionmap prevents the detach procedure')
