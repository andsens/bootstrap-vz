from base import Task
from common import phases
from common.tasks import packages


class ImagePackages(Task):
	description = 'Determining required image packages'
	phase = phases.preparation
	predecessors = [packages.ImagePackages]

	def run(self, info):
		manifest = info.manifest
		include, exclude = info.img_packages
		# Add some basic packages we are going to need
		include.add('grub2')

		# In squeeze, we need a special kernel flavor for xen
		kernels = {'squeeze': {'amd64': 'linux-image-amd64',
		                       'i386':  'linux-image-686', },
		           'wheezy':  {'amd64': 'linux-image-amd64',
		                       'i386':  'linux-image-686', }, }
		include.add(kernels.get(manifest.system['release']).get(manifest.system['architecture']))
