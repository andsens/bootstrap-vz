from bootstrapvz.base import Task
from .. import phases
import os


class RemoveDNSInfo(Task):
	description = 'Removing resolv.conf'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		if os.path.isfile(os.path.join(info.root, 'etc/resolv.conf')):
			os.remove(os.path.join(info.root, 'etc/resolv.conf'))


class RemoveHostname(Task):
	description = 'Removing the hostname file'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		if os.path.isfile(os.path.join(info.root, 'etc/hostname')):
			os.remove(os.path.join(info.root, 'etc/hostname'))


class ConfigureNetworkIF(Task):
	description = 'Configuring network interfaces'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		network_config_path = os.path.join(os.path.dirname(__file__), 'network-configuration.json')
		from ..tools import config_get
		if_config = config_get(network_config_path, [info.release_codename])

		interfaces_path = os.path.join(info.root, 'etc/network/interfaces')
		with open(interfaces_path, 'a') as interfaces:
			interfaces.write('\n'.join(if_config) + '\n')
