from base import Task
from common import phases
from common.tasks import network
from common.tasks import apt
import os.path


class AptSources(Task):
	description = 'Adding additional aptitude sources'
	phase = phases.system_modification
	predecessors = [apt.AptSources]
	successors = [apt.AptUpdate]

	def run(self, info):
		manifest_vars = {'release':      info.manifest.system['release'],
		                 'architecture': info.manifest.system['architecture'],
		                 'apt_mirror':   'http://http.debian.net/debian'}
		for name in info.manifest.plugins['packages']['sources'].iterkeys():
			list_path = os.path.join(info.root, 'etc/apt/sources.list.d/', name + '.list')
			with open(list_path, 'a') as source_list:
				for line in info.manifest.plugins['packages']['sources'][name]:
					source_list.write('{line}\n'.format(line=line.format(**manifest_vars)))


class InstallRemotePackages(Task):
	description = 'Installing remote packages'
	phase = phases.system_modification
	predecessors = [apt.AptUpdate, apt.DisableDaemonAutostart]
	successors = [network.RemoveDNSInfo]

	def run(self, info):
		manifest_vars = {'release':      info.manifest.system['release'],
		                 'architecture': info.manifest.system['architecture']}
		from common.tools import log_check_call
		for package in info.manifest.plugins['packages']['remote']:
			target_release = []
			if isinstance(package, basestring):
				name = package
			else:
				name = package['name'].format(**manifest_vars)
				if hasattr(package, 'target'):
					target = package['target'].format(**manifest_vars)
					target_release = ['--targe-release', target]
			log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', 'install',
			                '--assume-yes'] + target_release + [name])


class InstallLocalPackages(Task):
	description = 'Installing local packages'
	phase = phases.system_modification

	def run(self, info):
		from shutil import copy
		from os import remove
		from common.tools import log_check_call

		for package_src in info.manifest.plugins['packages']['local']:
			pkg_name = os.path.basename(package_src)
			package_dst = os.path.join('/tmp', pkg_name)
			copy(package_src, os.path.join(info.root, package_dst))
			log_check_call(['/usr/sbin/chroot', info.root,
			                '/usr/bin/dpkg', '--install', package_dst])
			remove(package_dst)
