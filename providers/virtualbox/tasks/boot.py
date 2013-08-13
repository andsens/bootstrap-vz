from base import Task
from common import phases


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification

	def run(self, info):
		import stat
	        rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP                | stat.S_IXGRP |
                     stat.S_IROTH                | stat.S_IXOTH)
        	x_all = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
		import os.path
		device_map_path = os.path.join(info.root, 'boot/grub/device.map')
		with open(device_map_path, 'w') as device_map:
			device_map.write('(hd0)   /dev/sda\n')

		from common.tools import log_check_call

		from shutil import copy
        	script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/grub.d/10_linux'))
        	script_dst = os.path.join(info.root, 'etc/grub.d/10_linux')
        	copy(script_src, script_dst)
        	os.chmod(script_dst, rwxr_xr_x)
                script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/grub.d/00_header'))
                script_dst = os.path.join(info.root, 'etc/grub.d/00_header')
                copy(script_src, script_dst)
                os.chmod(script_dst, rwxr_xr_x)
		log_check_call(['/usr/sbin/chroot', info.root, 'update-initramfs', '-u'])
		# Install grub in mbr
		log_check_call(['/usr/sbin/grub-install', '--boot-directory='+info.root+"/boot/", info.bootstrap_device['path']])

		log_check_call(['/usr/sbin/chroot', info.root, '/usr/sbin/update-grub'])
