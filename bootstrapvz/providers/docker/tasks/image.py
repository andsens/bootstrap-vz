from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tools import log_check_call


class CreateDockerfileEntry(Task):
	description = 'Creating the Dockerfile entry'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		info._docker['dockerfile'] = ''


class CreateImage(Task):
	description = 'Creating docker image'
	phase = phases.image_registration

	@classmethod
	def run(cls, info):
		from pipes import quote
		tar_cmd = ['tar', '--create', '--numeric-owner',
		           '--directory', info.volume.path, '.']
		docker_cmd = ['docker', 'import', '--change', info._docker['dockerfile'], '-',
		              info.manifest.name.format(**info.manifest_vars)]
		cmd = ' '.join(map(quote, tar_cmd)) + ' | ' + ' '.join(map(quote, docker_cmd))
		[info._docker['image_id']] = log_check_call([cmd], shell=True)


class PopulateLabels(Task):
	description = 'Populating docker labels'
	phase = phases.image_registration
	successors = [CreateImage]

	@classmethod
	def run(cls, info):
		import pyrfc3339
		from datetime import datetime
		import pytz
		labels = {}
		labels['name'] = info.manifest.name.format(**info.manifest_vars)
		# Inspired by https://github.com/projectatomic/ContainerApplicationGenericLabels
		# See here for the discussion on the debian-cloud mailing list
		# https://lists.debian.org/debian-cloud/2015/05/msg00071.html
		labels['architecture'] = info.manifest.system['architecture']
		labels['build-date'] = pyrfc3339.generate(datetime.utcnow().replace(tzinfo=pytz.utc))
		if 'labels' in info.manifest.provider:
			for label, value in info.manifest.provider['labels'].items():
				labels[label] = value.format(**info.manifest_vars)

		# pipes.quote converts newlines into \n rather than just prefixing
		# it with a backslash, so we need to escape manually
		def escape(value):
			value = value.replace('"', '\\"')
			value = value.replace('\n', '\\\n')
			value = '"' + value + '"'
			return value
		kv_pairs = [label + '=' + escape(value) for label, value in labels.items()]
		# Add some nice newlines and indentation
		info._docker['dockerfile'] += 'LABEL ' + ' \\\n      '.join(kv_pairs) + '\n'


class AppendManifestDockerfile(Task):
	description = 'Appending Dockerfile instructions from the manifest'
	phase = phases.image_registration
	predecessors = [PopulateLabels]
	successors = [CreateImage]

	@classmethod
	def run(cls, info):
		info._docker['dockerfile'] += info.manifest.provider['dockerfile'] + '\n'
