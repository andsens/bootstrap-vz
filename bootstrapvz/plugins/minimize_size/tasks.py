from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import bootstrap
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import host
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tools import sed_i
from bootstrapvz.common.tools import log_check_call
import os
import shutil

assets = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets'))
folders = ['tmp', 'var/lib/apt/lists']


class AddFolderMounts(Task):
	description = 'Mounting folders for writing temporary and cache data'
	phase = phases.os_installation
	predecessors = [bootstrap.Bootstrap]

	@classmethod
	def run(cls, info):
		info._minimize_size['foldermounts'] = os.path.join(info.workspace, 'minimize_size')
		os.mkdir(info._minimize_size['foldermounts'])
		for folder in folders:
			temp_path = os.path.join(info._minimize_size['foldermounts'], folder.replace('/', '_'))
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
			temp_path = os.path.join(info._minimize_size['foldermounts'], folder.replace('/', '_'))
			full_path = os.path.join(info.root, folder)

			info.volume.partition_map.root.remove_mount(full_path)
			shutil.rmtree(temp_path)

		os.rmdir(info._minimize_size['foldermounts'])
		del info._minimize_size['foldermounts']


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
	description = 'Zeroing unused blocks on the root partition'
	phase = phases.volume_unmounting
	predecessors = [filesystem.UnmountRoot]
	successors = [partitioning.UnmapPartitions, volume.Detach]

	@classmethod
	def run(cls, info):
		log_check_call(['zerofree', info.volume.partition_map.root.device_path])


class ShrinkVolume(Task):
	description = 'Shrinking the volume'
	phase = phases.volume_unmounting
	predecessors = [volume.Detach]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_check_call
		perm = os.stat(info.volume.image_path).st_mode & 0777
		log_check_call(['/usr/bin/vmware-vdiskmanager', '-k', info.volume.image_path])
		os.chmod(info.volume.image_path, perm)


class AutomateAptClean(Task):
	description = 'Configuring apt to always clean everything out when it\'s done'
	phase = phases.package_installation
	successors = [apt.AptUpdate]
	# Snatched from:
	# https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

	@classmethod
	def run(cls, info):
		shutil.copy(os.path.join(assets, 'apt-clean'),
		            os.path.join(info.root, 'etc/apt/apt.conf.d/90clean'))


class FilterTranslationFiles(Task):
	description = 'Configuring apt to only download and use specific translation files'
	phase = phases.package_installation
	successors = [apt.AptUpdate]
	# Snatched from:
	# https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

	@classmethod
	def run(cls, info):
		langs = info.manifest.plugins['minimize_size']['apt']['languages']
		config = '; '.join(map(lambda l: '"' + l + '"', langs))
		config_path = os.path.join(info.root, 'etc/apt/apt.conf.d/20languages')
		shutil.copy(os.path.join(assets, 'apt-languages'), config_path)
		sed_i(config_path, r'ACQUIRE_LANGUAGES_FILTER', config)


class AptGzipIndexes(Task):
	description = 'Configuring apt to always gzip lists files'
	phase = phases.package_installation
	successors = [apt.AptUpdate]
	# Snatched from:
	# https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

	@classmethod
	def run(cls, info):
		shutil.copy(os.path.join(assets, 'apt-gzip-indexes'),
		            os.path.join(info.root, 'etc/apt/apt.conf.d/20gzip-indexes'))


class AptAutoremoveSuggests(Task):
	description = 'Configuring apt to not consider suggested important'
	phase = phases.package_installation
	successors = [apt.AptUpdate]
	# Snatched from:
	# https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

	@classmethod
	def run(cls, info):
		shutil.copy(os.path.join(assets, 'apt-autoremove-suggests'),
		            os.path.join(info.root, 'etc/apt/apt.conf.d/20autoremove-suggests'))
