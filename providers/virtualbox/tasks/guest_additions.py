from base import Task
from common import phases
from common.tasks.packages import ImagePackages
from common.tasks.host import CheckPackages
from common.tasks.filesystem import FStab
from common.exceptions import TaskError


class CheckGuestAdditionsPath(Task):
	description = 'Checking whether the VirtualBox Guest Additions image exists'
	phase = phases.preparation

	def run(self, info):
		import os.path
		guest_additions_path = info.manifest.bootstrapper['guest_additions']
		if not os.path.exists(guest_additions_path):
			msg = 'The file {file} does not exist.'.format(file=guest_additions_path)
			raise TaskError(msg)


class AddGuestAdditionsPackages(Task):
	description = 'Adding packages to support Guest Additions installation'
	phase = phases.preparation
	predecessors = [ImagePackages]
	successors = [CheckPackages]

	def run(self, info):
		info.img_packages[0].update(['bzip2',
		                             'build-essential',
		                             'dkms',
		                             ])


class InstallGuestAdditions(Task):
	description = 'Installing the VirtualBox Guest Additions'
	phase = phases.system_modification
	predecessors = [FStab]

	def run(self, info):
		import os
		from common.tools import log_call
		guest_additions_path = info.manifest.bootstrapper['guest_additions']
		mount_dir = 'mnt/guest_additions'
		mount_path = os.path.join(info.root, mount_dir)
		os.mkdir(mount_path)
		root = info.volume.partition_map.root
		root.add_mount(guest_additions_path, mount_path, ['-o', 'loop'])

		install_script = os.path.join('/', mount_dir, 'VBoxLinuxAdditions.run')
		# Install will exit with $?=1 because X11 isn't installed
		log_call(['/usr/sbin/chroot', info.root,
		          install_script, '--nox11'])

		root.remove_mount(mount_path)
		os.rmdir(mount_path)
