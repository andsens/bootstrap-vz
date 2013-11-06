from base import Task
from common import phases
import os.path


class RemoveDNSInfo(Task):
	description = 'Removing resolv.conf'
	phase = phases.system_modification

	def run(self, info):
		from os import remove
		remove(os.path.join(info.root, 'etc/resolv.conf'))


class RemoveHostname(Task):
	description = 'Removing the hostname file'
	phase = phases.system_modification

	def run(self, info):
		from os import remove
		remove(os.path.join(info.root, 'etc/hostname'))


class ConfigureNetworkIF(Task):
	description = 'Configuring network interfaces'
	phase = phases.system_modification

	def run(self, info):
		interfaces_path = os.path.join(info.root, 'etc/network/interfaces')
		if_config = {'squeeze': ('auto lo\n'
		                         'iface lo inet loopback\n'
		                         'auto eth0\n'
		                         'iface eth0 inet dhcp\n'),
		             'wheezy':  'auto eth0\n'
		                        'iface eth0 inet dhcp\n'}
		with open(interfaces_path, 'a') as interfaces:
			interfaces.write(if_config.get(info.manifest.system['release']))
