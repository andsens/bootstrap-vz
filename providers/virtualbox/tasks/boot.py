from base import Task
from common import phases


class ConfigureGrub(Task):
	description = 'Configuring grub'
	phase = phases.system_modification

	def run(self, info):
		from common.tools import log_check_call
		log_check_call(['/usr/sbin/chroot', info.root, 'update-initramfs', '-u'])
		log_check_call(['/usr/sbin/grub-install',
		                '--boot-directory='+info.root+"/boot/",
		                info.bootstrap_device['path']])

		log_check_call(['/usr/sbin/chroot', info.root, '/usr/sbin/update-grub'])
