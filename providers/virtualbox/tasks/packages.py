from base import Task
from common import phases
from common.tasks import packages
from common.tasks.host import CheckPackages


class HostPackages(Task):
	description = 'Determining required host packages'
	phase = phases.preparation
	before = [CheckPackages]
	after = [packages.HostPackages]

	def run(self, info):
		info.host_packages.update(['qemu-utils', 'parted', 'kpartx', 'sysv-rc'])
		if 'xfs' in (p.filesystem for p in info.volume.partition_map.partitions):
			info.host_packages.add('xfsprogs')


class ImagePackages(Task):
	description = 'Determining required image packages'
	phase = phases.preparation
	after = [packages.ImagePackages]

	def run(self, info):
		manifest = info.manifest
		include, exclude = info.img_packages
		# Add some basic packages we are going to need
		include.update(['grub2'])

		# In squeeze, we need a special kernel flavor for xen
		kernels = {'squeeze': {'amd64': 'linux-image-amd64',
		                       'i386':  'linux-image-686', },
		           'wheezy':  {'amd64': 'linux-image-amd64',
		                       'i386':  'linux-image-686', }, }
		include.add(kernels.get(manifest.system['release']).get(manifest.system['architecture']))
