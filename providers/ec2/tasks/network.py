from base import Task
from common import phases
import os.path


class RemoveDNSInfo(Task):
	description = 'Removing resolv.conf'
	phase = phases.system_modification

	def run(self, info):
		from os import remove
		remove(os.path.join(info.root, 'etc/resolv.conf'))


class ConfigureNetworkIF(Task):
	description = 'Configuring network interfaces'
	phase = phases.system_modification

	def run(self, info):
		interfaces_path = os.path.join(info.root, 'etc/network/interfaces')
		if_config = {'squeeze': ('auto lo\niface lo inet loopback\n'
		                         'auto eth0\niface eth0 inet dhcp'),
		             'wheezy':  'auto eth0\niface eth0 inet dhcp'}
		with open(interfaces_path, 'a') as interfaces:
			interfaces.write(if_config.get(info.manifest.system['release']))


class ConfigureDHCP(Task):
	description = 'Configuring the DHCP client'
	phase = phases.system_modification

	def run(self, info):
		from common.tools import sed_i
		dhcpcd = os.path.join(info.root, 'etc/default/dhcpcd')
		sed_i(dhcpcd, '^#*SET_DNS=.*', 'SET_DNS=\'yes\'')
