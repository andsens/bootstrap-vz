from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import kernel
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
	description = 'Installing enhanced networking kernel driver using DKMS'
	phase = phases.system_modification
	successors = [kernel.UpdateInitramfs]

	@classmethod
	def run(cls, info):
		version = '2.15.3'
		drivers_url = 'http://downloads.sourceforge.net/project/e1000/ixgbevf stable/%s/ixgbevf-%s.tar.gz' % (version, version)
		archive = os.path.join(info.root, 'tmp', 'ixgbevf-%s.tar.gz' % (version))
		module_path = os.path.join(info.root, 'usr', 'src', 'ixgbevf-%s' % (version))

		import urllib
		urllib.urlretrieve(drivers_url, archive)

		from bootstrapvz.common.tools import log_check_call
		log_check_call(['tar', '--ungzip',
		                       '--extract',
		                       '--file', archive,
		                       '--directory', os.path.join(info.root, 'usr', 'src')])

		with open(os.path.join(module_path, 'dkms.conf'), 'w') as dkms_conf:
			dkms_conf.write("""PACKAGE_NAME="ixgbevf"
PACKAGE_VERSION="%s"
CLEAN="cd src/; make clean"
MAKE="cd src/; make BUILD_KERNEL=${kernelver}"
BUILT_MODULE_LOCATION[0]="src/"
BUILT_MODULE_NAME[0]="ixgbevf"
DEST_MODULE_LOCATION[0]="/updates"
DEST_MODULE_NAME[0]="ixgbevf"
AUTOINSTALL="yes"
""" % (version))

		for task in ['add', 'build', 'install']:
			# Invoke DKMS task using specified kernel module (-m) and version (-v)
			log_check_call(['chroot', info.root,
			                'dkms', task, '-m', 'ixgbevf', '-v', version])
