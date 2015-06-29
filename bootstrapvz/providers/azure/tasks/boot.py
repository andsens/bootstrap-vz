from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import grub
from bootstrapvz.common.tasks import kernel
import os


class PatchUdev(Task):
	description = 'Patching udev configuration to remove ROOTDELAY sleep'
	phase = phases.system_modification
	successors = [kernel.UpdateInitramfs]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_check_call
		from . import assets
		# c.f. http://anonscm.debian.org/cgit/pkg-systemd/systemd.git/commit/?id=61e055638cea
		with open(os.path.join(assets, 'udev.diff')) as diff_file:
			udev_dir = os.path.join(info.root, 'usr/share/initramfs-tools/scripts/init-top')
			log_check_call(['patch', '--no-backup-if-mismatch', '-p6', '-d' + udev_dir], stdin=diff_file)


class ConfigureGrub(Task):
	description = 'Change grub configuration to allow for ttyS0 output'
	phase = phases.system_modification
	successors = [grub.InstallGrub_1_99, grub.InstallGrub_2]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		grub_config = os.path.join(info.root, 'etc/default/grub')
		sed_i(grub_config, r'^(GRUB_CMDLINE_LINUX*=".*)"\s*$', r'\1console=ttyS0 earlyprintk=ttyS0 rootdelay=300"')
		sed_i(grub_config, r'^.*(GRUB_TIMEOUT=).*$', r'GRUB_TIMEOUT=0')
