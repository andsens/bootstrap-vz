from bootstrapvz.base import Task
from .. import phases
from ..tasks import packages


class AddDKMSPackages(Task):
	description = 'Adding DKMS and kernel header packages'
	phase = phases.package_installation
	successors = [packages.InstallPackages]

	@classmethod
	def run(cls, info):
		info.packages.add('dkms')
		kernel_pkg_arch = {'i386': '686-pae', 'amd64': 'amd64'}[info.manifest.system['architecture']]
		info.packages.add('linux-headers-' + kernel_pkg_arch)


class UpdateInitramfs(Task):
	description = 'Rebuilding initramfs'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_check_call
	        # Update initramfs (-u) for all currently installed kernel versions (-k all)
		log_check_call(['chroot', info.root, 'update-initramfs', '-u', '-k', 'all'])
