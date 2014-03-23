from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt


class DefaultPackages(Task):
	description = 'Adding image packages required for virtualbox'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		kernels = {'amd64': 'linux-image-amd64',
		           'i386':  'linux-image-686', }
		info.packages.add(kernels.get(info.manifest.system['architecture']))
