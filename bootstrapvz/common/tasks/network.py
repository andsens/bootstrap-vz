from bootstrapvz.base import Task
from .. import phases
import os


class RemoveDNSInfo(Task):
	description = 'Removing resolv.conf'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		if os.path.isfile(os.path.join(info.root, 'etc/resolv.conf')):
			os.remove(os.path.join(info.root, 'etc/resolv.conf'))


class RemoveHostname(Task):
	description = 'Removing the hostname file'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		if os.path.isfile(os.path.join(info.root, 'etc/hostname')):
			os.remove(os.path.join(info.root, 'etc/hostname'))


class SetHostname(Task):
	description = 'Writing hostname into the hostname file'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		hostname = info.manifest.system['hostname'].format(**info.manifest_vars)
		hostname_file_path = os.path.join(info.root, 'etc/hostname')
		with open(hostname_file_path, 'w') as hostname_file:
			hostname_file.write(hostname)

		hosts_path = os.path.join(info.root, 'etc/hosts')
		from bootstrapvz.common.tools import sed_i
		sed_i(hosts_path, '^127.0.0.1\tlocalhost$', '127.0.0.1\tlocalhost\n127.0.1.1\t' + hostname)


class ConfigureNetworkIF(Task):
	description = 'Configuring network interfaces'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		network_config_path = os.path.join(os.path.dirname(__file__), 'network-configuration.yml')
		from ..tools import config_get
		if_config = config_get(network_config_path, [info.release_codename])

		interfaces_path = os.path.join(info.root, 'etc/network/interfaces')
		with open(interfaces_path, 'a') as interfaces:
			interfaces.write(if_config + '\n')
