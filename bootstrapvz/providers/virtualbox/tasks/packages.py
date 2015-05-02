from bootstrapvz.base import Task
from bootstrapvz.common import phases


class DefaultPackages(Task):
	description = 'Adding image packages required for virtualbox'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		import os.path
		kernel_packages_path = os.path.join(os.path.dirname(__file__), 'packages-kernels.yml')
		from bootstrapvz.common.tools import config_get
		kernel_package = config_get(kernel_packages_path, [info.manifest.release.codename,
		                                                   info.manifest.system['architecture']])
		info.packages.add(kernel_package)
