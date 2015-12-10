from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import bootstrap
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import host
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import workspace
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
		perm = os.stat(info.volume.image_path).st_mode & 0777
		log_check_call(['/usr/bin/vmware-vdiskmanager', '-k', info.volume.image_path])
		os.chmod(info.volume.image_path, perm)


class CreateBootstrapFilterScripts(Task):
	description = 'Creating the bootstrapping locales filter script'
	phase = phases.os_installation
	successors = [bootstrap.Bootstrap]
	# Inspired by:
	# https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

	@classmethod
	def run(cls, info):
		if info.bootstrap_script is not None:
			from bootstrapvz.common.exceptions import TaskError
			raise TaskError('info.bootstrap_script seems to already be set '
			                'and is conflicting with this task')

		bootstrap_script = os.path.join(info.workspace, 'bootstrap_script.sh')
		filter_script = os.path.join(info.workspace, 'bootstrap_files_filter.sh')

		shutil.copy(os.path.join(assets, 'bootstrap-script.sh'), bootstrap_script)
		shutil.copy(os.path.join(assets, 'bootstrap-files-filter.sh'), filter_script)

		sed_i(bootstrap_script, r'BOOTSTRAP_FILES_FILTER_PATH', filter_script)
		sed_i(filter_script, r'EXCLUDE_PATTERN', "./usr/share/locale/.\+\|./usr/share/man/.\+")

		keep_files = ['./usr/share/locale/locale.alias',
		              './usr/share/man/man1',
		              './usr/share/man/man2',
		              './usr/share/man/man3',
		              './usr/share/man/man4',
		              './usr/share/man/man5',
		              './usr/share/man/man6',
		              './usr/share/man/man7',
		              './usr/share/man/man8',
		              './usr/share/man/man9',
		              ]
		locales = info.manifest.plugins['minimize_size']['apt']['locales']
		keep_files.extend(map(lambda l: './usr/share/locale/' + l + '/', locales))
		keep_files.extend(map(lambda l: './usr/share/man/' + l + '/', locales))

		sed_i(filter_script, r'INCLUDE_PATHS', "\n".join(keep_files))
		os.chmod(filter_script, 0755)

		info.bootstrap_script = bootstrap_script
		info._minimize_size['filter_script'] = filter_script


class DeleteBootstrapFilterScripts(Task):
	description = 'Deleting the bootstrapping locales filter script'
	phase = phases.cleaning
	successors = [workspace.DeleteWorkspace]

	@classmethod
	def run(cls, info):
		os.remove(info._minimize_size['filter_script'])
		del info._minimize_size['filter_script']
		os.remove(info.bootstrap_script)


class FilterLocales(Task):
	description = 'Configuring dpkg to only include specific locales/manpages when installing packages'
	phase = phases.os_installation
	successors = [bootstrap.Bootstrap]
	# Snatched from:
	# https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap
	# and
	# https://raphaelhertzog.com/2010/11/15/save-disk-space-by-excluding-useless-files-with-dpkg/

	@classmethod
	def run(cls, info):
		# This is before we start bootstrapping, so we create dpkg.cfg.d manually
		os.makedirs(os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d'))

		locale_lines = ['path-exclude=/usr/share/locale/*',
		                'path-include=/usr/share/locale/locale.alias']
		manpages_lines = ['path-exclude=/usr/share/man/*',
		                  'path-include=/usr/share/man/man[1-9]']

		locales = info.manifest.plugins['minimize_size']['apt']['locales']
		locale_lines.extend(map(lambda l: 'path-include=/usr/share/locale/' + l + '/*', locales))
		manpages_lines.extend(map(lambda l: 'path-include=/usr/share/man/' + l + '/*', locales))

		locales_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d/10filter-locales')
		manpages_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d/10filter-manpages')

		with open(locales_path, 'w') as locale_filter:
			locale_filter.write('\n'.join(locale_lines) + '\n')
		with open(manpages_path, 'w') as manpages_filter:
			manpages_filter.write('\n'.join(manpages_lines) + '\n')


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
