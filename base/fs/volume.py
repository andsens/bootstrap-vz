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
		self.specials_mounted = False
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

	def can_mount_specials(self):
		return self.is_state('attached')

	def mount_specials(self):
		if self.specials_mounted:
			raise VolumeError('The special devices are already mounted')
		root = self.partition_map.root.mount_dir
		log_check_call(['/bin/mount', '--bind', '/dev', '{root}/dev'.format(root=root)])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'proc', 'none', '/proc'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'sysfs', 'none', '/sys'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'devpts', 'none', '/dev/pts'])
		self.specials_mounted = True

	def unmount_specials(self):
		if not self.specials_mounted:
			raise VolumeError('The special devices are not mounted')
		root = self.partition_map.root.mount_dir
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/dev/pts'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/sys'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/proc'])
		log_check_call(['/bin/umount', '{root}/dev'.format(root=root)])
		self.specials_mounted = False

	def _check_blocking(self, e):
		if self.partition_map.is_blocking():
			raise VolumeError('The partitionmap prevents the detach procedure')
		if self.specials_mounted:
			raise VolumeError('The special devices are mounted and prevent the detaching procedure')
