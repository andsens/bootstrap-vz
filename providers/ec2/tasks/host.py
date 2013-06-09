from common import Task


class GetInfo(Task):
	def run(self, info):
		super(GetInfo, self).run(info)
		# import urllib2
		# import json
		# response = urllib2.urlopen('http://169.254.169.254/latest/dynamic/instance-identity/document')
		# info.host = json.load(response.read())
		# return info


class InstallPackages(Task):
	def run(self, info):
		# Check if packages are installed with
		# /usr/bin/dpkg -s ${name} | grep -q 'Status: install'
		pass
