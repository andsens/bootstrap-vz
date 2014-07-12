from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tools import log_check_call
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import locale
import logging
import os.path


class AddCloudInitPackages(Task):
	description = 'Adding cloud-init package and sudo'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources, apt.AddBackports]

	@classmethod
	def run(cls, info):
		target = None
		if info.release_codename == 'wheezy':
			target = '{system.release}-backports'
		info.packages.add('cloud-init', target)
		info.packages.add('sudo')


class SetUsername(Task):
	description = 'Setting username in cloud.cfg'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
		username = info.manifest.plugins['cloud_init']['username']
		search = '^     name: debian$'
		replace = ('     name: {username}\n'
		           '     sudo: ALL=(ALL) NOPASSWD:ALL\n'
		           '     shell: /bin/bash').format(username=username)
		sed_i(cloud_cfg, search, replace)


class SetMetadataSource(Task):
	description = 'Setting metadata source'
	phase = phases.package_installation
	predecessors = [locale.GenerateLocale]
	successors = [apt.AptUpdate]

	@classmethod
	def run(cls, info):
		if 'metadata_sources' in info.manifest.plugins['cloud_init']:
			sources = info.manifest.plugins['cloud_init']['metadata_sources']
		else:
			source_mapping = {'ec2': 'Ec2'}
			sources = source_mapping.get(info.manifest.provider['name'], None)
			if sources is None:
				msg = ('No cloud-init metadata source mapping found for provider `{provider}\', '
				       'skipping selections setting.').format(provider=info.manifest.provider['name'])
				logging.getLogger(__name__).warn(msg)
				return
		sources = "cloud-init	cloud-init/datasources	multiselect	" + sources
		log_check_call(['chroot', info.root, 'debconf-set-selections'], sources)


class DisableModules(Task):
	description = 'Setting cloud.cfg modules'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		import re
		patterns = ""
		for pattern in info.manifest.plugins['cloud_init']['disable_modules']:
			if patterns != "":
				patterns = patterns + "|" + pattern
			else:
				patterns = "^\s+-\s+(" + pattern
		patterns = patterns + ")$"
		regex = re.compile(patterns)

		cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
		import fileinput
		for line in fileinput.input(files=cloud_cfg, inplace=True):
			if not regex.match(line):
				print line,
