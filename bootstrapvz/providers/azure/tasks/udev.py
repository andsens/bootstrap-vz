from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import kernel
from bootstrapvz.common.tools import log_check_call
import os.path
from . import assets


class PatchUdev(Task):
	description = 'Patch udev configuration to remove ROOTDELAY sleep'
	phase = phases.system_modification
	successors = [kernel.UpdateInitramfs]

	@classmethod
	def run(cls, info):
		# c.f. http://anonscm.debian.org/cgit/pkg-systemd/systemd.git/commit/?id=61e055638cea
		with open(os.path.join(assets, 'udev.diff')) as diff_file:
			udev_dir = os.path.join(info.root, 'usr/share/initramfs-tools/scripts/init-top')
			log_check_call(['patch', '--no-backup-if-mismatch', '-p6', '-d' + udev_dir], stdin=diff_file)
