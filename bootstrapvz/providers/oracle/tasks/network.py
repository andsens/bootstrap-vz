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


class SetCloudInitMetadataURL(Task):
	description = 'Setting cloud-init metadata URL'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		cfg_src = os.path.join(assets, 'cloud-init/90_dpkg.cfg')
		cfg_dst = os.path.join(info.root, 'etc/cloud/cloud.cfg.d/90_dpkg.cfg')
		shutil.copy(cfg_src, cfg_dst)
