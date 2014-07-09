from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import boot


class ConfigureGrub(Task):
	description = 'Change grub configuration to allow for ttyS0 output'
	phase = phases.system_modification
	successors = [boot.InstallGrub_1_99, boot.InstallGrub_2]

	@classmethod
	def run(cls, info):
		import os
		from bootstrapvz.common.tools import sed_i
		grub_config = os.path.join(info.root, 'etc/default/grub')
		sed_i(grub_config, r'^(GRUB_CMDLINE_LINUX*=".*)"\s*$', r'\1console=ttyS0 earlyprintk=ttyS0 rootdelay=300"')
		sed_i(grub_config, r'^.*(GRUB_TIMEOUT=).*$', r'GRUB_TIMEOUT=0')
