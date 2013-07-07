from base import Task
from common import phases
import os.path


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification

	def run(self, info):
		import stat
		rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		             stat.S_IRGRP                | stat.S_IXGRP |
		             stat.S_IROTH                | stat.S_IXOTH)
		x_all = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

		import os
		import glob
		grub2_cfgs = glob.glob(os.path.join(info.root, 'etc/grub.d/*'))
		for cfg in grub2_cfgs:
			os.chmod(cfg, os.stat(cfg).st_mode & ~ x_all)

		from shutil import copy
		script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/grub.d/40_custom'))
		script_dst = os.path.join(info.root, 'etc/grub.d/40_custom')
		copy(script_src, script_dst)
		os.chmod(script_dst, rwxr_xr_x)

		from common.tools import sed_i
		grub_def = os.path.join(info.root, 'etc/default/grub')
		sed_i(grub_def, '^GRUB_TIMEOUT=[0-9]+', 'GRUB_TIMEOUT=0\nGRUB_HIDDEN_TIMEOUT=true')

		from common.tools import log_check_call
		log_check_call(['chroot', info.root, 'update-grub'])
		log_check_call(['chroot', info.root, 'ln', '-s', '/boot/grub/grub.cfg', '/boot/grub/menu.lst'])


class BlackListModules(Task):
	description = 'Blacklisting kernel modules'
	phase = phases.system_modification

	def run(self, info):
		blacklist_path = os.path.join(info.root, 'etc/modprobe.d/blacklist.conf')
		with open(blacklist_path, 'a') as blacklist:
			blacklist.write('# disable pc speaker\nblacklist pcspkr')


class DisableGetTTYs(Task):
	description = 'Disabling getty processes'
	phase = phases.system_modification

	def run(self, info):
		from common.tools import sed_i
		inittab_path = os.path.join(info.root, 'etc/inittab')
		tty1 = '1:2345:respawn:/sbin/getty 38400 tty1'
		sed_i(inittab_path, '^'+tty1, '#'+tty1)
		ttyx = ':23:respawn:/sbin/getty 38400 tty'
		for i in range(2, 6):
			i = str(i)
			sed_i(inittab_path, '^'+i+ttyx+i, '#'+i+ttyx+i)
