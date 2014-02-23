from base import Task
from common import phases
import os

assets = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets'))


class AddONEContextPackage(Task):
	description = 'Adding the OpenNebula context package'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		package = os.path.join(assets, 'one-context_3.8.1.deb')
		info.packages.add_local(package)


class OpenNebulaContext(Task):
	description = 'Setup OpenNebula init context'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		# Fix start
		from common.tools import sed_i
		vmcontext_def = os.path.join(info.root, 'etc/init.d/vmcontext')
		sed_i(vmcontext_def, '# Default-Start:', '# Default-Start: 2 3 4 5')

		from common.tools import log_check_call
		log_check_call(['chroot', info.root, 'update-rc.d', 'vmcontext', 'start',
		                '90', '2', '3', '4', '5', 'stop', '90', '0', '6'])

		from shutil import copy
		# Load all pubkeys in root authorized_keys
		script_src = os.path.join(assets, 'one-pubkey.sh')
		script_dst = os.path.join(info.root, 'etc/one-context.d/one-pubkey.sh')
		copy(script_src, script_dst)

		# If USER_EC2_DATA is a script, execute it
		script_src = os.path.join(assets, 'one-ec2.sh')
		script_dst = os.path.join(info.root, 'etc/one-context.d/one-ec2.sh')
		copy(script_src, script_dst)
