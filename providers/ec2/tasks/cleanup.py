from base import Task
from common import phases
import os


class ClearMOTD(Task):
	description = 'Clearing the MOTD'
	phase = phases.system_cleaning

	def run(self, info):
		with open('/var/run/motd', 'w'):
			pass


class ShredHostkeys(Task):
	description = 'Securely deleting ssh hostkeys'
	phase = phases.system_cleaning

	def run(self, info):
		ssh_hostkeys = ['ssh_host_dsa_key',
		                'ssh_host_rsa_key']
		if info.manifest.system['release'] != 'squeeze':
			ssh_hostkeys.append('ssh_host_ecdsa_key')

		private = [os.path.join(info.root, 'etc/ssh', name) for name in ssh_hostkeys]
		public = [path + '.pub' for path in private]

		from common.tools import log_check_call
		log_check_call(['/usr/bin/shred', '--remove'] + private + public)


class CleanTMP(Task):
	description = 'Removing temporary files'
	phase = phases.system_cleaning

	def run(self, info):
		import glob
		tmp_files = glob.glob(os.path.join(info.root, 'tmp/*'))
		for tmp_file in tmp_files:
			os.remove(tmp_file)

		log_files = glob.glob(os.path.join(info.root, 'var/log/{bootstrap,dpkg}.log'))
		for log_file in log_files:
			os.remove(log_file)
