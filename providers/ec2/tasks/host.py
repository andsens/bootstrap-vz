from base import Task
from common import phases
import packages


class CheckPackages(Task):
	description = 'Checking installed host packages'
	phase = phases.preparation
	after = [packages.HostPackages, packages.ImagePackages]

	def run(self, info):
		import subprocess
		from os import devnull
		for package in info.host_packages:
			try:
				with open(devnull, 'w') as dev_null:
					subprocess.check_call(['/usr/bin/dpkg', '-s', package], stdout=dev_null, stderr=dev_null)
			except subprocess.CalledProcessError:
				msg = "The package ``{0}\'\' is not installed".format(package)
				raise RuntimeError(msg)


class GetInfo(Task):
	description = 'Retrieving instance metadata'
	phase = phases.preparation

	def run(self, info):
		super(GetInfo, self).run(info)
		import urllib2
		import json
		metadata_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
		response = urllib2.urlopen(url=metadata_url, timeout=5)
		info.host = json.load(response)
		return info
