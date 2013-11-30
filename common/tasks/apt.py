from base import Task
from common import phases
from common.tools import log_check_call
import network
import locale
import os


class AptSources(Task):
	description = 'Adding aptitude sources'
	phase = phases.system_modification

	def run(self, info):
		sources_path = os.path.join(info.root, 'etc/apt/sources.list')
		with open(sources_path, 'w') as apt_sources:
			apt_sources.write(('deb     {apt_mirror} {release} main\n'
			                   'deb-src {apt_mirror} {release} main\n'
			                   .format(apt_mirror='http://http.debian.net/debian',
			                           release=info.manifest.system['release'])))
			apt_sources.write(('deb     {apt_mirror} {release}/updates main\n'
			                   'deb-src {apt_mirror} {release}/updates main\n'
			                   .format(apt_mirror='http://security.debian.org/',
			                           release=info.manifest.system['release'])))


class DisableDaemonAutostart(Task):
	description = 'Disabling daemon autostart'
	phase = phases.system_modification

	def run(self, info):
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
	phase = phases.system_modification
	predecessors = [locale.GenerateLocale, AptSources]
	successors = [network.RemoveDNSInfo]

	def run(self, info):
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', 'update'])
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get',
		                                               '--fix-broken',
		                                               '--assume-yes',
		                                               'install'])
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', '--assume-yes', 'upgrade'])


class AptUpgrade(Task):
	description = 'Upgrading packages and fixing broken dependencies'
	phase = phases.system_modification
	predecessors = [AptUpdate, DisableDaemonAutostart]
	successors = [network.RemoveDNSInfo]

	def run(self, info):
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', 'update'])
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get',
		                                               '--fix-broken',
		                                               '--assume-yes',
		                                               'install'])
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', '--assume-yes', 'upgrade'])


class PurgeUnusedPackages(Task):
	description = 'Removing unused packages'
	phase = phases.system_cleaning

	def run(self, info):
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', 'autoremove', '--purge'])


class AptClean(Task):
	description = 'Clearing the aptitude cache'
	phase = phases.system_cleaning

	def run(self, info):
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', 'clean'])

		lists = os.path.join(info.root, 'var/lib/apt/lists')
		for list_file in [os.path.join(lists, f) for f in os.listdir(lists)]:
			if os.path.isfile(list_file):
				os.remove(list_file)


class EnableDaemonAutostart(Task):
	description = 'Re-enabling daemon autostart after installation'
	phase = phases.system_cleaning

	def run(self, info):
		os.remove(os.path.join(info.root, 'usr/sbin/policy-rc.d'))
