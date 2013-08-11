from base import Task
from common import phases


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification

	def run(self, info):
		import os.path
		device_map_path = os.path.join(info.root, 'boot/grub/device.map')
		with open(device_map_path, 'w') as device_map:
			device_map.write(('(hd0)   {dev_path}\n'
			                  '(hd0,1) {root_path}'
			                  .format(dev_path=info.bootstrap_device['path'],
			                          root_path=info.bootstrap_device['partitions']['root_path'])))

		from common.tools import log_check_call
		log_check_call(['/usr/sbin/chroot', info.root, 'update-initramfs', '-u'])

		log_check_call(['/usr/sbin/chroot', info.root,
		                '/usr/sbin/grub-mkconfig', '-o', '/boot/grub/grub.cfg'])

		log_check_call(['/usr/sbin/chroot', info.root,
		                '/usr/sbin/grub-install', info.bootstrap_device['path']])
