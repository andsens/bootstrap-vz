from bootstrapvz.base import Task
from bootstrapvz.common.tasks import apt
from bootstrapvz.common import phases


class AddONEContextPackage(Task):
	description = 'Adding the OpenNebula context package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources, apt.AddBackports]

	@classmethod
	def run(cls, info):
		target = None
		if info.release_codename == 'wheezy':
			target = '{system.release}-backports'
		info.packages.add('opennebula-context', target)
