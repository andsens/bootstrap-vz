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
		udev_file = os.path.join(info.root, 'usr/share/initramfs-tools/scripts/init-top/udev')
		diff_file = os.path.join(assets, 'udev.diff')
		log_check_call(['patch', '--no-backup-if-mismatch', udev_file, diff_file])


class ConfigureGrub(Task):
	description = 'Change grub configuration to allow for ttyS0 output'
	phase = phases.system_modification
	predecessors = [grub.ConfigureGrub]
	successors = [grub.InstallGrub_1_99, grub.InstallGrub_2]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		grub_config = os.path.join(info.root, 'etc/default/grub')
		sed_i(grub_config, r'^(GRUB_CMDLINE_LINUX_DEFAULT=.*)', r'GRUB_CMDLINE_LINUX_DEFAULT=""')
		sed_i(grub_config, r'^(GRUB_CMDLINE_LINUX*=".*)"\s*$', r'\1console=tty0 console=ttyS0,115200n8 earlyprintk=ttyS0,115200 rootdelay=300"')
		sed_i(grub_config, r'^(GRUB_HIDDEN_TIMEOUT=).*', r'#GRUB_HIDDEN_TIMEOUT=true')
		sed_i(grub_config, r'^.*(GRUB_TIMEOUT=).*$', r'GRUB_TIMEOUT=5')
