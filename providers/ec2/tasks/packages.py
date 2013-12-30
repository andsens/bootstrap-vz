from base import Task
from common import phases
from common.tasks import apt


class DefaultPackages(Task):
	description = 'Adding image packages required for EC2'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	def run(self, info):
		info.packages.add('openssh-server')
		info.packages.add('file')  # Needed for the init scripts
		info.packages.add('dhcpcd')  # isc-dhcp-client doesn't work properly with ec2

		info.exclude_packages.add('isc-dhcp-client')
		info.exclude_packages.add('isc-dhcp-common')

		# In squeeze, we need a special kernel flavor for xen
		kernels = {'squeeze': {'amd64': 'linux-image-xen-amd64',
		                       'i386':  'linux-image-xen-686', },
		           'wheezy':  {'amd64': 'linux-image-amd64',
		                       'i386':  'linux-image-686', }, }
		kernel_package = kernels.get(info.manifest.system['release']).get(info.manifest.system['architecture'])
		info.packages.add(kernel_package)
