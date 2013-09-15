from abc import ABCMeta
from fysom import Fysom


class Volume(object):

	__metaclass__ = ABCMeta

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'detached'},
	          {'name': 'attach', 'src': 'detached', 'dst': 'attached'},
	          {'name': 'partition', 'src': 'attached', 'dst': 'partitioned'},
	          {'name': 'map', 'src': 'partitioned', 'dst': 'mapped'},
	          {'name': 'format', 'src': 'mapped', 'dst': 'formatted'},
	          {'name': 'mount', 'src': ['formatted', 'mounted'], 'dst': 'mounted'},
	          {'name': 'unmount', 'src': 'mounted', 'dst': 'formatted'},
	          {'name': 'unmap', 'src': 'formatted', 'dst': 'partitioned_fmt'},
	          {'name': 'detach', 'src': 'partitioned_fmt', 'dst': 'detached_fmt'},
	          {'name': 'delete', 'src': ['detached', 'detached_prt', 'detached_fmt'], 'dst': 'deleted'},

	          {'name': 'attach', 'src': 'detached_fmt', 'dst': 'partitioned_fmt'},
	          {'name': 'map', 'src': 'partitioned_fmt', 'dst': 'formatted'},

	          {'name': 'attach', 'src': 'detached_prt', 'dst': 'partitioned'},
	          {'name': 'detach', 'src': 'partitioned', 'dst': 'detached_prt'},

	          {'name': 'detach', 'src': 'attached', 'dst': 'detached'},
	          {'name': 'unmap', 'src': 'mapped', 'dst': 'partitioned'},
	          ]

	mount_events = [{'name': 'mount_root', 'src': 'unmounted', 'dst': 'root_mounted'},
	                {'name': 'mount_boot', 'src': 'root_mounted', 'dst': 'boot_mounted'},
	                {'name': 'mount_specials', 'src': 'boot_mounted', 'dst': 'specials_mounted'},
	                {'name': 'unmount_specials', 'src': 'specials_mounted', 'dst': 'boot_mounted'},
	                {'name': 'unmount_boot', 'src': 'boot_mounted', 'dst': 'root_mounted'},
	                {'name': 'unmount_root', 'src': 'root_mounted', 'dst': 'unmounted'},

	                {'name': 'mount_specials', 'src': 'root_mounted', 'dst': 'specials_mounted_no_boot'},
	                {'name': 'mount_boot', 'src': 'specials_mounted_no_boot', 'dst': 'specials_mounted'},
	                {'name': 'unmount_specials', 'src': 'specials_mounted_no_boot', 'dst': 'root_mounted'},
	                {'name': 'unmount_boot', 'src': 'specials_mounted', 'dst': 'specials_mounted_no_boot'},
	                ]

	def __init__(self, partition_map, callbacks={}):
		self.device_path = None
		self.partition_map = partition_map
		self.size = self.partition_map.get_total_size()

		callbacks.update({'onbeforepartition': self._partition,
		                  'onbeforemap': self._map,
		                  'onbeforeunmap': self._unmap,
		                  'onbeforeformat': self._format,
		                  'onbeforeunmount': self._unmount,
		                  })

		mount_callbacks = {'onbeforemount_root': self._mount_root,
		                   'onbeforemount_boot': self._mount_boot,
		                   'onbeforemount_specials': self._mount_specials,
		                   'onbeforeunmount_root': self._unmount_root,
		                   'onbeforeunmount_boot': self._unmount_boot,
		                   'onbeforeunmount_specials': self._unmount_specials,
		                   }
		self.fsm = Fysom({'initial': 'nonexistent',
		                  'events': self.events,
		                  'callbacks': callbacks})

		self.mount_fsm = Fysom({'initial': 'unmounted',
		                        'events': self.mount_events,
		                        'callbacks': mount_callbacks})

		from common.fsm import attach_proxy_methods
		attach_proxy_methods(self, self.events, self.fsm)
		attach_proxy_methods(self, self.mount_events, self.mount_fsm)

	def state(self):
		return self.fsm.current

	def force_state(self, state):
		self.fsm.current = state

	def _partition(self, e):
		self.partition_map.create(self)

	def _map(self, e):
		self.partition_map.map(self)

	def _unmap(self, e):
		self.partition_map.unmap(self)

	def _format(self, e):
		self.partition_map.format()

	def _unmount(self, e):
		if self.mount_fsm.current is 'specials_mounted':
			self.unmount_specials()
		if self.mount_fsm.current is 'specials_mounted_no_boot':
			self.unmount_specials()
		if self.mount_fsm.current is 'boot_mounted':
			self.unmount_boot()
		if self.mount_fsm.current is 'root_mounted':
			self.unmount_root()

	def mount_root(self, destination):
		self.mount_fsm.mount_root(destination=destination)

	def unmount_root(self):
		self.mount_fsm.unmount_root()
		self.fsm.unmount()

	def _mount_root(self, e):
		self.mount()
		self.partition_map.mount_root(e.destination)

	def _unmount_root(self, e):
		self.partition_map.unmount_root()

	def _mount_boot(self, e):
		self.mount()
		self.partition_map.mount_boot()

	def _unmount_boot(self, e):
		self.partition_map.unmount_boot()

	def _mount_specials(self, e):
		self.mount()
		from common.tools import log_check_call
		root = self.partition_map.root.mount_dir
		log_check_call(['/bin/mount', '--bind', '/dev', '{root}/dev'.format(root=root)])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'proc', 'none', '/proc'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'sysfs', 'none', '/sys'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/mount', '--types', 'devpts', 'none', '/dev/pts'])

	def _unmount_specials(self, e):
		from common.tools import log_check_call
		root = self.partition_map.root.mount_dir
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/dev/pts'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/sys'])
		log_check_call(['/usr/sbin/chroot', root, '/bin/umount', '/proc'])
		log_check_call(['/bin/umount', '{root}/dev'.format(root=root)])
