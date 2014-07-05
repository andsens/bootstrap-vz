from bootstrapvz.base import Task
from bootstrapvz.common import phases
import os


class VirtIO(Task):
	description = 'Install virtio modules'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		modules = os.path.join(info.root, '/etc/initramfs-tools/modules')
		with open(modules, "a") as modules_file:
			modules_file.write("\n")
			for module in info.manifest.provider.get('virtio', []):
				modules_file.write(module + "\n")
