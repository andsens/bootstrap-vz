from base import Task
from common import phases
from common.tasks import apt


class InstallRemotePackages(Task):
	description = 'Installing remote packages'
	phase = phases.package_installation
	predecessors = [apt.AptUpgrade]

	def run(self, info):
		if len(info.packages.remote) == 0:
			return
		import os
		from common.tools import log_check_call

		packages = []
		for name, target in info.packages.remote.iteritems():
			packages.append('{name}/{target}'.format(name=name, target=target))

		env = os.environ.copy()
		env['DEBIAN_FRONTEND'] = 'noninteractive'
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-get', 'install',
		                '--assume-yes'] + packages,
		               env=env)


class InstallLocalPackages(Task):
	description = 'Installing local packages'
	phase = phases.package_installation
	predecessors = [apt.AptUpgrade]
	successors = [InstallRemotePackages]

	def run(self, info):
		if len(info.packages.local) == 0:
			return
		from shutil import copy
		from common.tools import log_check_call
		import os

		for package_src in info.packages.local:
			pkg_name = os.path.basename(package_src)
			package_dst = os.path.join('/tmp', pkg_name)
			copy(package_src, os.path.join(info.root, package_dst))

			env = os.environ.copy()
			env['DEBIAN_FRONTEND'] = 'noninteractive'
			log_check_call(['/usr/sbin/chroot', info.root,
			                '/usr/bin/dpkg', '--install', package_dst],
			               env=env)
			os.remove(package_dst)
