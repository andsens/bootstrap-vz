from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt


class DefaultPackages(Task):
	description = 'Adding image packages required for EC2'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('openssh-server')
		info.packages.add('file')  # Needed for the init scripts
		info.packages.add('dhcpcd')  # isc-dhcp-client doesn't work properly with ec2

		info.exclude_packages.add('isc-dhcp-client')
		info.exclude_packages.add('isc-dhcp-common')

		import os.path
		kernel_packages_path = os.path.join(os.path.dirname(__file__), 'packages-kernels.json')
		from bootstrapvz.common.tools import config_get
		kernel_package = config_get(kernel_packages_path, [info.release_codename,
		                                                   info.manifest.system['architecture']])
		info.packages.add(kernel_package)
