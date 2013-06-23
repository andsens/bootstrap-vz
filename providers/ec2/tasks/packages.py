from base import Task
from common import phases


class HostPackages(Task):
	description = 'Determining required host packages'
	phase = phases.preparation

	def run(self, info):
		super(HostPackages, self).run(info)
		packages = set(['debootstrap',
		                # To make sure a volume is not busy before unmounting we need lsof
		                'lsof',
		                ])
		if info.manifest.volume['filesystem'] == 'xfs':
			packages.add('xfsprogs')

		info.host_packages = packages


class ImagePackages(Task):
	description = 'Determining required image packages'
	phase = phases.preparation

	def run(self, info):
		super(ImagePackages, self).run(info)
		manifest = info.manifest
		# Add some basic packages we are going to need
		include = set(['udev',
		               'openssh-server',
		               # We could bootstrap without locales, but things just suck without them, error messages etc.
		               'locales',
		               # Needed for the init scripts
		               'file',
		               # isc-dhcp-client doesn't work properly with ec2
		               'dhcpcd',
		               ])

		if manifest.virtualization == 'pvm':
			include.add('grub-pc')
		
		exclude = set(['isc-dhcp-client',
		               'isc-dhcp-common',
		               ])
		
		# In squeeze, we need a special kernel flavor for xen
		kernels = {'squeeze': {'amd64': 'linux-image-xen-amd64',
		                       'i386':  'linux-image-xen-686', },
		           'wheezy':  {'amd64': 'linux-image-amd64',
		                       'i386':  'linux-image-686', }, }
		include.add(kernels.get(manifest.system['release']).get(manifest.system['architecture']))
		
		include = include.union(manifest.system['packages'])
		
		info.img_packages = include, exclude
