from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import os.path
from . import assets
import apt
import initd


class AddOpenSSHPackage(Task):
	description = 'Adding openssh package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('openssh-server')


class AddSSHKeyGeneration(Task):
	description = 'Adding SSH private key generation init scripts'
	phase = phases.system_modification
	successors = [initd.InstallInitScripts]

	@classmethod
	def run(cls, info):
		init_scripts_dir = os.path.join(assets, 'init.d')
		install = info.initd['install']
		from subprocess import CalledProcessError
		try:
			log_check_call(['chroot', info.root,
			                'dpkg-query', '-W', 'openssh-server'])
			if info.release_codename == 'squeeze':
				install['generate-ssh-hostkeys'] = os.path.join(init_scripts_dir, 'squeeze/generate-ssh-hostkeys')
			else:
				install['generate-ssh-hostkeys'] = os.path.join(init_scripts_dir, 'generate-ssh-hostkeys')
		except CalledProcessError:
			import logging
			logging.getLogger(__name__).warn('The OpenSSH server has not been installed, '
			                                 'not installing SSH host key generation script.')


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


class ShredHostkeys(Task):
	description = 'Securely deleting ssh hostkeys'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		ssh_hostkeys = ['ssh_host_dsa_key',
		                'ssh_host_rsa_key']
		if info.release_codename != 'squeeze':
			ssh_hostkeys.append('ssh_host_ecdsa_key')

		private = [os.path.join(info.root, 'etc/ssh', name) for name in ssh_hostkeys]
		public = [path + '.pub' for path in private]

		from ..tools import log_check_call
		log_check_call(['shred', '--remove'] + private + public)
