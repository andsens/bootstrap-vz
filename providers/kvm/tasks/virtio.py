from base import Task
from common import phases
from common.tasks.packages import InstallPackages
from common.exceptions import TaskError
import os


class VirtIO(Task):
	description = 'Install virtio modules'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from common.tools import log_call
		modules = os.path.join(info.root,'/etc/initramfs-tools/modules')
		with open(modules, "a") as modules_file:
			modules_file.write("\n");
			for module in info.manifest.bootstrapper.get('virtio', []):
				modules_file.write(module+"\n")
