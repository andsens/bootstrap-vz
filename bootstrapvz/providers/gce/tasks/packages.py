from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import packages
from bootstrapvz.common.tools import config_get
import logging
import os


class DefaultPackages(Task):
	description = 'Adding image packages required for GCE'
	phase = phases.preparation
	successors = [packages.AddManifestPackages]

	@classmethod
	def run(cls, info):
		info.packages.add('acpi-support-base')
		info.packages.add('busybox')
		info.packages.add('ca-certificates')
		info.packages.add('curl')
		info.packages.add('ethtool')
		info.packages.add('gdisk')
		info.packages.add('kpartx')
		info.packages.add('isc-dhcp-client')
		info.packages.add('lsb-release')
		info.packages.add('ntp')
		info.packages.add('parted')
		info.packages.add('python')
		info.packages.add('openssh-client')
		info.packages.add('openssh-server')
		info.packages.add('sudo')
		info.packages.add('uuid-runtime')

		kernel_packages_path = os.path.join(os.path.dirname(__file__), 'packages-kernels.yml')
		kernel_package = config_get(kernel_packages_path, [info.manifest.release.codename,
		                                                   info.manifest.system['architecture']])
		info.packages.add(kernel_package)


class ReleasePackages(Task):
	description = 'Adding release-specific packages required for GCE'
	phase = phases.preparation
	predecessors = [apt.AddBackports, DefaultPackages]
	successors = [packages.AddManifestPackages]

	@classmethod
	def run(cls, info):
		# Add release-specific packages, if available.
		if (info.source_lists.target_exists('wheezy-backports') or
		        info.source_lists.target_exists('jessie') or
		        info.source_lists.target_exists('jessie-backports')):
			info.packages.add('cloud-initramfs-growroot')
		else:
			msg = ('No release-specific packages found for {system.release}').format(**info.manifest_vars)
			logging.getLogger(__name__).warning(msg)


class GooglePackages(Task):
	description = 'Adding image packages required for GCE from Google repositories'
	phase = phases.preparation
	predecessors = [DefaultPackages]
	successors = [packages.AddManifestPackages]

	@classmethod
	def run(cls, info):
		info.packages.add('google-compute-daemon')
		info.packages.add('google-startup-scripts')
		info.packages.add('python-gcimagebundle')
