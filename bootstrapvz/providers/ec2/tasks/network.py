from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
import os.path


class EnableDHCPCDDNS(Task):
	description = 'Configuring the DHCP client to set the nameservers'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		# The dhcp client that ships with debian sets the DNS servers per default.
		# For dhcpcd in Wheezy and earlier we need to configure it to do that.
		if info.release_codename not in {'jessie', 'sid'}:
			from bootstrapvz.common.tools import sed_i
			dhcpcd = os.path.join(info.root, 'etc/default/dhcpcd')
			sed_i(dhcpcd, '^#*SET_DNS=.*', 'SET_DNS=\'yes\'')


class AddBuildEssentialPackage(Task):
	description = 'Adding build-essential package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('build-essential')


class InstallEnhancedNetworking(Task):
	description = 'Installing network drivers for SR-IOV support'
	phase = phases.package_installation

	@classmethod
	def run(cls, info):
		drivers_url = 'http://downloads.sourceforge.net/project/e1000/ixgbevf stable/2.11.3/ixgbevf-2.11.3.tar.gz'
		archive = os.path.join(info.root, 'tmp', 'ixgbevf-2.11.3.tar.gz')

		import urllib
		urllib.urlretrieve(drivers_url, archive)

		from bootstrapvz.common.tools import log_check_call
		log_check_call('tar', '--ungzip',
		                      '--extract',
		                      '--file', archive,
		                      '--directory', os.path.join(info.root, 'tmp'))

		src_dir = os.path.join('/tmp', os.path.basename(drivers_url), 'src')
		log_check_call(['chroot', info.root,
		                'make', '--directory', src_dir])
		log_check_call(['chroot', info.root,
		                'make', 'install',
		                        '--directory', src_dir])

		ixgbevf_conf_path = os.path.join(info.root, 'etc/modprobe.d/ixgbevf.conf')
		with open(ixgbevf_conf_path, 'w') as ixgbevf_conf:
			ixgbevf_conf.write('options ixgbevf InterruptThrottleRate=1,1,1,1,1,1,1,1')
