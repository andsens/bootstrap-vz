from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import initd
import os
import os.path
import shutil

ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets'))


class AddDockerDeps(Task):
	description = 'Add packages for docker deps'
	phase = phases.package_installation
	DOCKER_DEPS = ['aufs-tools', 'btrfs-tools', 'git', 'iptables',
	               'procps', 'xz-utils', 'ca-certificates']

	@classmethod
	def run(cls, info):
		for pkg in cls.DOCKER_DEPS:
			info.packages.add(pkg)


class AddDockerBinary(Task):
	description = 'Add docker binary'
	phase = phases.system_modification
	DOCKER_URL = 'https://get.docker.io/builds/Linux/x86_64/docker-latest'

	@classmethod
	def run(cls, info):
		import urllib
		bin_docker = os.path.join(info.root, 'usr/bin/docker')
		urllib.urlretrieve(cls.DOCKER_URL, bin_docker)
		os.chmod(bin_docker, 0755)


class AddDockerInit(Task):
	description = 'Add docker init script'
	phase = phases.system_modification
	successors = [initd.InstallInitScripts]

	@classmethod
	def run(cls, info):
		init_src = os.path.join(ASSETS_DIR, 'init.d/docker')
		info.initd['install']['docker'] = init_src
		default_src = os.path.join(ASSETS_DIR, 'default/docker')
		default_dest = os.path.join(info.root, 'etc/default/docker')
		shutil.copy(default_src, default_dest)
