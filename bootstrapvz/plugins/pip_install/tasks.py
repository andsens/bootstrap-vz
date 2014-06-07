from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import network
from bootstrapvz.common.tasks import packages
from bootstrapvz.common.tasks import apt


class AddPipPackage(Task):
	description = 'Adding `pip\' and Co. to the image packages'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]
	successors = [packages.InstallPackages]

	@classmethod
	def run(cls, info):
		for package_name in ('python-pip', 'build-essential', 'python-dev'):
			info.packages.add(package_name)


class PipInstallCommand(Task):
	description = 'Install python packages from pypi with pip'
	phase = phases.system_modification
	successors = [network.RemoveDNSInfo]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_check_call
		packages = info.manifest.plugins['pip_install']['packages']
		pip_install_command = ['chroot', info.root, 'pip', 'install']
		pip_install_command.extend(packages)
		log_check_call(pip_install_command)
