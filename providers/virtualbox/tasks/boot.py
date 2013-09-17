from base import Task
from common import phases
from common.tasks import apt
from common.fs.loopbackvolume import LoopbackVolume


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification
	after = [apt.AptUpgrade]

	def run(self, info):
		import os
		from common.tools import log_check_call

		boot_dir = os.path.join(info.root, 'boot')
		grub_dir = os.path.join(boot_dir, 'grub')

		# if type(info.volume) is LoopbackVolume:
		if isinstance(info.volume, LoopbackVolume):
			# GRUB cannot deal with installing to loopback devices
			# so we fake a real harddisk with dmsetup.
			# Guide here: http://ebroder.net/2009/08/04/installing-grub-onto-a-disk-image/
			info.volume.unmount()
			info.volume.unmap()
			info.volume.link_dm_node()
			info.volume.map()
			info.volume.mount_root(info.root)
			info.volume.mount_boot()
			info.volume.mount_specials()
		try:
			[device_path] = log_check_call(['readlink', '-f', info.volume.device_path])
			device_map_path = os.path.join(grub_dir, 'device.map')
			with open(device_map_path, 'w') as device_map:
				device_map.write('(hd0) {device_path}\n'.format(device_path=device_path))
				for idx, partition in enumerate(info.volume.partition_map.partitions):
					[partition_path] = log_check_call(['readlink', '-f', partition.device_path])
					device_map.write('(hd0,gpt{idx}) {device_path}\n'.format(device_path=partition_path, idx=idx+1))

			# Install grub
			log_check_call(['/usr/sbin/chroot', info.root,
			                '/usr/sbin/grub-install',
			                # '--root-directory=' + info.root,
			                # '--boot-directory=' + boot_dir,
			                device_path])
			log_check_call(['/usr/sbin/chroot', info.root, '/usr/sbin/update-grub'])
		except Exception as e:
			if isinstance(info.volume, LoopbackVolume):
				info.volume.unmount()
				info.volume.unmap()
				info.volume.unlink_dm_node()
				info.volume.map()
				info.volume.mount_root(info.root)
				info.volume.mount_boot()
				info.volume.mount_specials()
			raise e

		if isinstance(info.volume, LoopbackVolume):
			info.volume.unmount()
			info.volume.unmap()
			info.volume.unlink_dm_node()
			info.volume.map()
			info.volume.mount_root(info.root)
			info.volume.mount_boot()
			info.volume.mount_specials()
