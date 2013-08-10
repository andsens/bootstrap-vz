from base import Task
from common import phases
import os


class BlackListModules(Task):
	description = 'Blacklisting kernel modules'
	phase = phases.system_modification

	def run(self, info):
		blacklist_path = os.path.join(info.root, 'etc/modprobe.d/blacklist.conf')
		with open(blacklist_path, 'a') as blacklist:
			blacklist.write(('# disable pc speaker\n'
			                 'blacklist pcspkr'))


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
