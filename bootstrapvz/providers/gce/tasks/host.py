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


class InstallHostnameHook(Task):
	description = "Installing hostname hook"
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		# There's a surprising amount of software out there which doesn't react well to the system
		# hostname being set to a potentially long the fully qualified domain name, including Java 7
		# and lower, quite relevant to a lot of cloud use cases such as Hadoop. Since Google Compute
		# Engine's out-of-the-box domain names are long but predictable based on project name, we
		# install this hook to set the hostname to the short hostname but add a suitable /etc/hosts
		# entry.
		#
		# Since not all operating systems which Google supports on Compute Engine work with the
		# /etc/dhcp/dhclient-exit-hooks.d directory, Google's internally-built packaging uses the
		# consistent install path of /usr/share/google/set-hostname, and OS-specific build steps are
		# used to activate the DHCP hook. In any future Debian-maintained distro-specific packaging,
		# the updated deb could handle installing the below symlink or the script itself into
		# /etc/dhcp/dhclient-exit-hooks.d.
		log_check_call(['chroot', info.root, 'ln', '-s',
		                '/usr/share/google/set-hostname',
		                '/etc/dhcp/dhclient-exit-hooks.d/set-hostname'])
