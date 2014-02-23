from base import Task
from common import phases
from common.tasks import apt
from common.tasks import bootstrap
from common.tasks import filesystem
from common.tasks import host
from common.tasks import partitioning
from common.tasks import volume
import os

folders = ['tmp', 'var/lib/apt/lists']


class AddFolderMounts(Task):
	description = 'Mounting folders for writing temporary and cache data'
	phase = phases.os_installation
	predecessors = [bootstrap.Bootstrap]

	@classmethod
	def run(cls, info):
		info.minimize_size_folder = os.path.join(info.workspace, 'minimize_size')
		os.mkdir(info.minimize_size_folder)
		for folder in folders:
			temp_path = os.path.join(info.minimize_size_folder, folder.replace('/', '_'))
			os.mkdir(temp_path)

			full_path = os.path.join(info.root, folder)
			info.volume.partition_map.root.add_mount(temp_path, full_path, ['--bind'])


class RemoveFolderMounts(Task):
	description = 'Removing folder mounts for temporary and cache data'
	phase = phases.system_cleaning
	successors = [apt.AptClean]

	@classmethod
	def run(cls, info):
		import shutil
		for folder in folders:
			temp_path = os.path.join(info.minimize_size_folder, folder.replace('/', '_'))
			full_path = os.path.join(info.root, folder)

			info.volume.partition_map.root.remove_mount(full_path)
			shutil.rmtree(temp_path)

		os.rmdir(info.minimize_size_folder)
		del info.minimize_size_folder


class AddRequiredCommands(Task):
	description = 'Adding commands required for reducing volume size'
	phase = phases.preparation
	successors = [host.CheckExternalCommands]

	@classmethod
	def run(cls, info):
		if info.manifest.plugins['minimize_size'].get('zerofree', False):
			info.host_dependencies['zerofree'] = 'zerofree'
		if info.manifest.plugins['minimize_size'].get('shrink', False):
			link = 'https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation/10_0'
			info.host_dependencies['vmware-vdiskmanager'] = link


class Zerofree(Task):
	description = 'Zeroing unused blocks on the volume'
	phase = phases.volume_unmounting
	predecessors = [filesystem.UnmountRoot, partitioning.UnmapPartitions]
	successors = [volume.Detach]

	@classmethod
	def run(cls, info):
		from common.tools import log_check_call
		log_check_call(['zerofree', info.volume.device_path])


class ShrinkVolume(Task):
	description = 'Shrinking the volume'
	phase = phases.volume_unmounting
	predecessors = [volume.Detach]

	@classmethod
	def run(cls, info):
		from common.tools import log_check_call
		log_check_call(['/usr/bin/vmware-vdiskmanager', '-k', info.volume.image_path])
