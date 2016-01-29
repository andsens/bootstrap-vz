from bootstrapvz.base import Task
from bootstrapvz.common import phases
from . import assets
import os.path
import shutil


class InstallDHCPCD(Task):
	description = 'Replacing isc-dhcp with dhcpcd5'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		info.packages.add('dhcpcd5')
		info.exclude_packages.add('isc-dhcp-client')
		info.exclude_packages.add('isc-dhcp-common')
