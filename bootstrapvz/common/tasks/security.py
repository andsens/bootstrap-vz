from bootstrapvz.base import Task
from .. import phases
import os.path


class EnableShadowConfig(Task):
	description = 'Enabling shadowconfig'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from ..tools import log_check_call
		log_check_call(['chroot', info.root, 'shadowconfig', 'on'])


class DisableSSHPasswordAuthentication(Task):
	description = 'Disabling SSH password authentication'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from ..tools import sed_i
		sshd_config_path = os.path.join(info.root, 'etc/ssh/sshd_config')
		sed_i(sshd_config_path, '^#PasswordAuthentication yes', 'PasswordAuthentication no')


class DisableSSHDNSLookup(Task):
	description = 'Disabling sshd remote host name lookup'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		sshd_config_path = os.path.join(info.root, 'etc/ssh/sshd_config')
		with open(sshd_config_path, 'a') as sshd_config:
			sshd_config.write('UseDNS no')
