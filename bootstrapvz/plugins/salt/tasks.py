from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import packages
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tools import log_check_call
from bootstrapvz.common.tools import sed_i
import os
import urllib


class InstallSaltDependencies(Task):
	description = 'Add depended packages for salt-minion'
	phase = phases.package_installation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('curl')
		info.packages.add('ca-certificates')


class BootstrapSaltMinion(Task):
	description = 'Installing salt-minion using the bootstrap script'
	phase = phases.package_installation
	predecessors = [packages.InstallPackages]

	@classmethod
	def run(cls, info):
		# Download bootstrap script
		bootstrap_script = os.path.join(info.root, 'install_salt.sh')
		with open(bootstrap_script, 'w') as f:
			d = urllib.urlopen('http://bootstrap.saltstack.org')
			f.write(d.read())

		# This is needed since bootstrap doesn't handle -X for debian distros properly.
		# We disable checking for running services at end since we do not start them.
		sed_i(bootstrap_script, 'install_debian_check_services', 'disabled_debian_check_services')

		bootstrap_command = ['chroot', info.root, 'bash', 'install_salt.sh', '-X']

		if 'master' in info.manifest.plugins['salt']:
			bootstrap_command.extend(['-A', info.manifest.plugins['salt']['master']])

		install_source = info.manifest.plugins['salt'].get('install_source', 'stable')

		bootstrap_command.append(install_source)
		if install_source == 'git' and ('version' in info.manifest.plugins['salt']):
			bootstrap_command.append(info.manifest.plugins['salt']['version'])
		log_check_call(bootstrap_command)


class SetSaltGrains(Task):
	description = 'Set custom salt grains'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		grains_file = os.path.join(info.root, 'etc/salt/grains')
		grains = info.manifest.plugins['salt']['grains']
		with open(grains_file, 'a') as f:
			for g in grains:
				f.write('%s: %s\n' % (g, grains[g]))
