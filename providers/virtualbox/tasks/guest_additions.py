from base import Task
from common import phases
from common.tasks.packages import InstallPackages
from common.exceptions import TaskError


class CheckGuestAdditionsPath(Task):
	description = 'Checking whether the VirtualBox Guest Additions image exists'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		import os.path
		guest_additions_path = info.manifest.bootstrapper['guest_additions']
		if not os.path.exists(guest_additions_path):
			msg = 'The file {file} does not exist.'.format(file=guest_additions_path)
			raise TaskError(msg)


class AddGuestAdditionsPackages(Task):
	description = 'Adding packages to support Guest Additions installation'
	phase = phases.package_installation
	successors = [InstallPackages]

	@classmethod
	def run(cls, info):
		info.packages.add('bzip2')
		info.packages.add('build-essential')
		info.packages.add('dkms')

		from common.tools import log_check_call
		[kernel_version] = log_check_call(['chroot', info.root,
		                                   'uname', '-r'])
		kernel_headers_pkg = 'linux-headers-{version}'.format(version=kernel_version)
		info.packages.add(kernel_headers_pkg)


class InstallGuestAdditions(Task):
	description = 'Installing the VirtualBox Guest Additions'
	phase = phases.package_installation
	predecessors = [InstallPackages]

	@classmethod
	def run(cls, info):
		import os
		guest_additions_path = info.manifest.bootstrapper['guest_additions']
		mount_dir = 'mnt/guest_additions'
		mount_path = os.path.join(info.root, mount_dir)
		os.mkdir(mount_path)
		root = info.volume.partition_map.root
		root.add_mount(guest_additions_path, mount_path, ['-o', 'loop'])

		install_script = os.path.join('/', mount_dir, 'VBoxLinuxAdditions.run')
		from common.tools import log_call
		status, out, err = log_call(['chroot', info.root,
		                            install_script, '--nox11'])
		# Install will exit with $?=1 because X11 isn't installed
		if status != 1:
			msg = ('VBoxLinuxAdditions.run exited with status {status}, '
			       'it should exit with status 1').format(status=status)
			raise TaskError(msg)

		root.remove_mount(mount_path)
		os.rmdir(mount_path)
