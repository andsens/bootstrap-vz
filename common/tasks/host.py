from base import Task
from common import phases
from common.exceptions import TaskError
import packages


class CheckPackages(Task):
	description = 'Checking installed host packages'
	phase = phases.preparation
	after = [packages.HostPackages, packages.ImagePackages]

	def run(self, info):
		from common.tools import log_check_call
		from subprocess import CalledProcessError
		for package in info.host_packages:
			try:
				log_check_call(['/usr/bin/dpkg-query', '-W', package])
			except CalledProcessError:
				msg = "The package ``{0}\'\' is not installed".format(package)
				raise TaskError(msg)
