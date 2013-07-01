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
				log_check_call(['/usr/bin/dpkg', '-s', package])
			except CalledProcessError:
				msg = "The package ``{0}\'\' is not installed".format(package)
				raise TaskError(msg)


class GetInfo(Task):
	description = 'Retrieving instance metadata'
	phase = phases.preparation

	def run(self, info):
		import urllib2
		import json
		metadata_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
		response = urllib2.urlopen(url=metadata_url, timeout=5)
		info.host = json.load(response)
		return info
