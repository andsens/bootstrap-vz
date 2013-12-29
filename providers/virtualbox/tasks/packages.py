from base import Task
from common import phases
from common.tasks import packages


class DefaultPackages(Task):
	description = 'Adding image packages required for virtualbox'
	phase = phases.preparation

	def run(self, info):
		# Add some basic packages we are going to need
		info.packages.add('grub2')

		kernels = {'amd64': 'linux-image-amd64',
		           'i386':  'linux-image-686', }
		info.packages.add(kernels.get(info.manifest.system['architecture']))
