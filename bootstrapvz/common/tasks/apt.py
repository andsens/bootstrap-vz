from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import locale
import os


class AddManifestSources(Task):
	description = 'Adding sources from the manifest'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		for name, lines in info.manifest.packages['sources'].iteritems():
			for line in lines:
				info.source_lists.add(name, line)


class AddDefaultSources(Task):
	description = 'Adding default release sources'
	phase = phases.preparation
	predecessors = [AddManifestSources]

	@classmethod
	def run(cls, info):
		components = ' '.join(info.manifest.packages.get('components', ['main']))
		info.source_lists.add('main', 'deb     {apt_mirror} {system.release} ' + components)
		info.source_lists.add('main', 'deb-src {apt_mirror} {system.release} ' + components)
		if info.release_codename != 'sid':
			info.source_lists.add('main', 'deb     http://security.debian.org/  {system.release}/updates ' + components)
			info.source_lists.add('main', 'deb-src http://security.debian.org/  {system.release}/updates ' + components)
			info.source_lists.add('main', 'deb     {apt_mirror} {system.release}-updates ' + components)
			info.source_lists.add('main', 'deb-src {apt_mirror} {system.release}-updates ' + components)


class AddManifestPreferences(Task):
	description = 'Adding preferences from the manifest'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		for name, preferences in info.manifest.packages['preferences'].iteritems():
                            info.preference_lists.add(name, preferences)


class InstallTrustedKeys(Task):
	description = 'Installing trusted keys'
	phase = phases.package_installation

	@classmethod
	def run(cls, info):
		from shutil import copy
		for key_path in info.manifest.packages['trusted-keys']:
			key_name = os.path.basename(key_path)
			destination = os.path.join(info.root, 'etc/apt/trusted.gpg.d', key_name)
			copy(key_path, destination)


class WriteSources(Task):
	description = 'Writing aptitude sources to disk'
	phase = phases.package_installation
	predecessors = [InstallTrustedKeys]

	@classmethod
	def run(cls, info):
		for name, sources in info.source_lists.sources.iteritems():
			if name == 'main':
				list_path = os.path.join(info.root, 'etc/apt/sources.list')
			else:
				list_path = os.path.join(info.root, 'etc/apt/sources.list.d/', name + '.list')
			with open(list_path, 'w') as source_list:
				for source in sources:
					source_list.write(str(source) + '\n')


class WritePreferences(Task):
	description = 'Writing aptitude preferences to disk'
	phase = phases.package_installation
	predecessors = [WriteSources]

	@classmethod
	def run(cls, info):
		for name, preferences in info.preference_lists.preferences.iteritems():
			if name == 'main':
				list_path = os.path.join(info.root, 'etc/apt/preferences')
			else:
				list_path = os.path.join(info.root, 'etc/apt/preferences.d/', name)
			with open(list_path, 'w') as preference_list:
				for preference in preferences:
					preference_list.write(str(preference) + '\n')


class DisableDaemonAutostart(Task):
	description = 'Disabling daemon autostart'
	phase = phases.package_installation

	@classmethod
	def run(cls, info):
		rc_policy_path = os.path.join(info.root, 'usr/sbin/policy-rc.d')
		with open(rc_policy_path, 'w') as rc_policy:
			rc_policy.write(('#!/bin/sh\n'
			                 'exit 101'))
		import stat
		os.chmod(rc_policy_path,
		         stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		         stat.S_IRGRP                | stat.S_IXGRP |
		         stat.S_IROTH                | stat.S_IXOTH)


class AptUpdate(Task):
	description = 'Updating the package cache'
	phase = phases.package_installation
	predecessors = [locale.GenerateLocale, WriteSources]

	@classmethod
	def run(cls, info):
		log_check_call(['chroot', info.root,
		                'apt-get', 'update'])


class AptUpgrade(Task):
	description = 'Upgrading packages and fixing broken dependencies'
	phase = phases.package_installation
	predecessors = [AptUpdate, DisableDaemonAutostart]

	@classmethod
	def run(cls, info):
		from subprocess import CalledProcessError
		try:
			log_check_call(['chroot', info.root,
			                'apt-get', 'install',
			                           '--fix-broken',
			                           '--no-install-recommends',
			                           '--assume-yes'])
			log_check_call(['chroot', info.root,
			                'apt-get', 'upgrade',
			                           '--no-install-recommends',
			                           '--assume-yes'])
		except CalledProcessError as e:
			if e.returncode == 100:
				import logging
				msg = ('apt exited with status code 100. '
				       'This can sometimes occur when package retrieval times out or a package extraction failed. '
				       'apt might succeed if you try bootstrapping again.')
				logging.getLogger(__name__).warn(msg)
			raise e


class PurgeUnusedPackages(Task):
	description = 'Removing unused packages'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		log_check_call(['chroot', info.root,
		                'apt-get', 'autoremove',
		                           '--purge',
		                           '--assume-yes'])


class AptClean(Task):
	description = 'Clearing the aptitude cache'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		log_check_call(['chroot', info.root,
		                'apt-get', 'clean'])

		lists = os.path.join(info.root, 'var/lib/apt/lists')
		for list_file in [os.path.join(lists, f) for f in os.listdir(lists)]:
			if os.path.isfile(list_file):
				os.remove(list_file)


class EnableDaemonAutostart(Task):
	description = 'Re-enabling daemon autostart after installation'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		os.remove(os.path.join(info.root, 'usr/sbin/policy-rc.d'))
