from base import Task
from common import phases


class HostPackages(Task):
	description = 'Determining required host packages'
	phase = phases.preparation

	def run(self, info):
		packages = set(['debootstrap'])
		info.host_packages = packages


class ImagePackages(Task):
	description = 'Determining required image packages'
	phase = phases.preparation

	def run(self, info):
		# Add some basic packages we are going to need
		include = set(['udev',
		               'openssh-server',
		               # We could bootstrap without locales, but things just suck without them, error messages etc.
		               'locales',
		               ])
		exclude = set()

		info.img_packages = include, exclude
