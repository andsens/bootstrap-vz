from base import Task
from common import phases
import os.path


class RemoveDNSInfo(Task):
	description = 'Removing resolv.conf'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from os import remove
		remove(os.path.join(info.root, 'etc/resolv.conf'))


class RemoveHostname(Task):
	description = 'Removing the hostname file'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from os import remove
		remove(os.path.join(info.root, 'etc/hostname'))


class ConfigureNetworkIF(Task):
	description = 'Configuring network interfaces'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		interfaces_path = os.path.join(info.root, 'etc/network/interfaces')
		if_config = []
		with open('common/tasks/network-configuration.json') as stream:
			import json
			if_config = json.loads(stream.read())
		with open(interfaces_path, 'a') as interfaces:
			interfaces.write('\n'.join(if_config.get(info.manifest.system['release'])) + '\n')
