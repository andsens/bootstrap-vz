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
		info.packages.add('openssl')
		info.packages.add('python-openssl')
		info.packages.add('python-pyasn1')
		info.packages.add('sudo')

		import os.path
		kernel_packages_path = os.path.join(os.path.dirname(__file__), 'packages-kernels.yml')
		from bootstrapvz.common.tools import config_get
		kernel_package = config_get(kernel_packages_path, [info.release_codename,
		                                                   info.manifest.system['architecture']])
		info.packages.add(kernel_package)


class Waagent(Task):
	description = 'Add waagent'
	phase = phases.package_installation
	predecessors = [InstallPackages]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_check_call
		import os
		waagent_version = info.manifest.provider['waagent']['version']
		waagent_file = 'WALinuxAgent-' + waagent_version + '.tar.gz'
		waagent_url = 'https://github.com/Azure/WALinuxAgent/archive/' + waagent_file
		log_check_call(['wget', '-P', info.root, waagent_url])
		waagent_directory = os.path.join(info.root, 'root')
		log_check_call(['tar', 'xaf', os.path.join(info.root, waagent_file), '-C', waagent_directory])
		os.remove(os.path.join(info.root, waagent_file))
		waagent_script = '/root/WALinuxAgent-WALinuxAgent-' + waagent_version + '/waagent'
		log_check_call(['chroot', info.root, 'cp', waagent_script, '/usr/sbin/waagent'])
		log_check_call(['chroot', info.root, 'chmod', '755', '/usr/sbin/waagent'])
		log_check_call(['chroot', info.root, 'waagent', '-install'])
		if info.manifest.system['waagent'].get('conf', False):
			if os.path.isfile(info.manifest.system['waagent']['conf']):
				log_check_call(['cp', info.manifest.system['waagent']['conf'],
				                os.path.join(info.root, 'etc/waagent.conf')])
