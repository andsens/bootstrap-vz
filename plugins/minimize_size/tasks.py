from base import Task
from common import phases
from common.tasks import bootstrap
from common.tasks import apt
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
