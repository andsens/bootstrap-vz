from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks.packages import InstallPackages


class DefaultPackages(Task):
	description = 'Adding image packages required for Azure'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		kernels = {'amd64': 'linux-image-amd64',
		           'i386':  'linux-image-686', }
		info.packages.add(kernels.get(info.manifest.system['architecture']))
		info.packages.add('openssl')
		info.packages.add('python-openssl')
		info.packages.add('openssh-server')
		info.packages.add('python-pyasn1')
		info.packages.add('git')
		info.packages.add('sudo')
		#info.packages.add('waagent')

class Waagent(Task):
	description = 'Add waagent'
	phase = phases.package_installation
	predecessors = [InstallPackages]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_call
		import os
		env = os.environ.copy()
		env['GIT_SSL_NO_VERIFY'] = 'true'
		status, out, err = log_call(['chroot', info.root,
         'git','clone', 'https://github.com/WindowsAzure/WALinuxAgent.git',
         '/root/WALinuxAgent'], env=env)
		status, out, err = log_call(['chroot', info.root,
         'cp','/root/WALinuxAgent/waagent','/usr/sbin/waagent'])
		status, out, err = log_call(['chroot', info.root,
         'chmod','755','/usr/sbin/waagent'])
		status, out, err = log_call(['chroot', info.root,
          '/usr/sbin/waagent','-install'])
		import os.path
		if hasattr(info.manifest, 'azure') and info.manifest.azure['waagent']:
			if os.path.isfile(info.manifest.azure['waagent']):
				status, out, err = log_call(['cp',
                                    info.manifest.azure['waagent'],
                                    os.path.join(info.root,'etc/waagent.conf')])

