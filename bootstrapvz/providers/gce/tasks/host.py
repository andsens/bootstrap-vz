from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import network
from bootstrapvz.common.tools import log_check_call
import os.path


class DisableIPv6(Task):
	description = "Disabling IPv6 support"
	phase = phases.system_modification
	predecessors = [network.ConfigureNetworkIF]

	@classmethod
	def run(cls, info):
		network_configuration_path = os.path.join(info.root, 'etc/sysctl.d/70-disable-ipv6.conf')
		with open(network_configuration_path, 'w') as config_file:
			print >>config_file, "net.ipv6.conf.all.disable_ipv6 = 1"


class SetHostname(Task):
	description = "Setting hostname"
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		log_check_call(['chroot', info.root, 'ln', '-s',
		                '/usr/share/google/set-hostname',
		                '/etc/dhcp/dhclient-exit-hooks.d/set-hostname'])
