from common import Task


class HostPackages(Task):
	def run(self, info):
		super(HostPackages, self).run(info)
		info.host_pkg = self.get_host_packages(info.manifest)
		return info

	def get_host_packages(self, manifest):
		packages = set(['debootstrap',
		                # To make sure a volume is not busy before unmounting we need lsof
		                'lsof',
		                ])
		if manifest.volume['filesystem'] == 'xfs':
			packages.add('xfsprogs')

		return packages


class ImagePackages(Task):
	def run(self, info):
		super(ImagePackages, self).run(info)
		info.image_pkg_include, info.image_pkg_exclude = self.get_image_packages(info.manifest)
		return info

	def get_image_packages(self, manifest):
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
		
		return include, exclude
