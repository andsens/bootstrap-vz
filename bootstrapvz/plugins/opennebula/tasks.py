from bootstrapvz.base import Task
from bootstrapvz.common.tasks import apt
from bootstrapvz.common import phases


class AddBackports(Task):
	description = 'Adding backports to the apt sources'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		if info.source_lists.target_exists('{system.release}-backports'):
			import logging
			msg = ('{system.release}-backports target already exists').format(**info.manifest_vars)
			logging.getLogger(__name__).info(msg)
		else:
			info.source_lists.add('backports', 'deb     {apt_mirror} {system.release}-backports main')
			info.source_lists.add('backports', 'deb-src {apt_mirror} {system.release}-backports main')


class AddONEContextPackage(Task):
	description = 'Adding the OpenNebula context package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources, AddBackports]

	@classmethod
	def run(cls, info):
		target = None
		if info.manifest.system['release'] in ['wheezy', 'stable']:
			target = '{system.release}-backports'
		info.packages.add('opennebula-context', target)
