from base import Task
from common import phases
from common.tasks import host


class HostDependencies(Task):
	description = 'Adding more required host packages'
	phase = phases.preparation
	successors = [host.CheckHostDependencies]

	def run(self, info):
		if info.manifest.volume['backing'] == 's3':
			info.host_dependencies.add('euca2ools')


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
