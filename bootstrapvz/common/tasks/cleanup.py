from bootstrapvz.base import Task
from .. import phases
import os
import shutil


class ClearMOTD(Task):
	description = 'Clearing the MOTD'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		with open('/var/run/motd', 'w'):
			pass


class ShredHostkeys(Task):
	description = 'Securely deleting ssh hostkeys'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		ssh_hostkeys = ['ssh_host_dsa_key',
		                'ssh_host_rsa_key']
		if info.manifest.system['release'] != 'squeeze':
			ssh_hostkeys.append('ssh_host_ecdsa_key')

		private = [os.path.join(info.root, 'etc/ssh', name) for name in ssh_hostkeys]
		public = [path + '.pub' for path in private]

		from ..tools import log_check_call
		log_check_call(['shred', '--remove'] + private + public)


class CleanTMP(Task):
	description = 'Removing temporary files'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		tmp = os.path.join(info.root, 'tmp')
		for tmp_file in [os.path.join(tmp, f) for f in os.listdir(tmp)]:
			if os.path.isfile(tmp_file):
				os.remove(tmp_file)
			else:
				shutil.rmtree(tmp_file)

		log = os.path.join(info.root, 'var/log/')
		os.remove(os.path.join(log, 'bootstrap.log'))
		os.remove(os.path.join(log, 'dpkg.log'))
