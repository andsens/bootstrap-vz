from base import Task
from common import phases
import os.path


class EnableDHCPCDDNS(Task):
	description = 'Configuring the DHCP client to set the nameservers'
	phase = phases.system_modification

	def run(self, info):
		# The dhcp client that ships with debian sets the DNS servers per default.
		# For dhcpcd we need to configure it to do that.
		from common.tools import sed_i
		dhcpcd = os.path.join(info.root, 'etc/default/dhcpcd')
		sed_i(dhcpcd, '^#*SET_DNS=.*', 'SET_DNS=\'yes\'')
