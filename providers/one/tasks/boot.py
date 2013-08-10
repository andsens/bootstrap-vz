from base import Task
from common import phases
import os


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification

	def run(self, info):
		import stat
		rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		             stat.S_IRGRP                | stat.S_IXGRP |
		             stat.S_IROTH                | stat.S_IXOTH)
		x_all = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

		grubd = os.path.join(info.root, 'etc/grub.d')
		for cfg in [os.path.join(grubd, f) for f in os.listdir(grubd)]:
			os.chmod(cfg, os.stat(cfg).st_mode & ~ x_all)

		from shutil import copy
		script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/grub.d/40_custom'))
		script_dst = os.path.join(info.root, 'etc/grub.d/40_custom')
		copy(script_src, script_dst)
		os.chmod(script_dst, rwxr_xr_x)

		if info.manifest.virtualization == 'virtio':
			modules_path = os.path.join(info.root, 'etc/initramfs-tools/modules')
			with open(modules_path, 'a') as modules:
				modules.write("\nvirtio_pci\nvirtio_blk\n")

		from common.tools import log_check_call
		log_check_call(['/usr/sbin/chroot', info.root, 'ln', '-s', '/boot/grub/grub.cfg', '/boot/grub/menu.lst'])

		log_check_call(['/usr/sbin/chroot', info.root, 'update-initramfs', '-u'])
		log_check_call(['grub-install', '--boot-directory='+info.root+"/boot/", '/dev/loop0'])

		log_check_call(['/usr/sbin/chroot', info.root, '/usr/sbin/update-grub'])

		from common.tools import sed_i
		if info.manifest.virtualization == 'virtio':
			grub_cfg = os.path.join(info.root, 'boot/grub/grub.cfg')
			sed_i(grub_cfg, 'sda', 'vda')
			device_map = os.path.join(info.root, 'boot/grub/device.map')
			sed_i(device_map, 'sda', 'vda')
