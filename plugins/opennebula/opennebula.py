from base import Task
from common import phases
import os
from providers.raw.tasks.locale import GenerateLocale


class OpenNebulaContext(Task):
	description = 'Setup OpenNebula init context'
	phase = phases.system_modification
        after = [GenerateLocale]

	def run(self, info):
		import stat
		rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		             stat.S_IRGRP                | stat.S_IXGRP |
		             stat.S_IROTH                | stat.S_IXOTH)

		from shutil import copy
		script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets/one-context_3.8.1.deb'))
		script_dst = os.path.join(info.root, 'tmp/one-context_3.8.1.deb')
		copy(script_src, script_dst)
		os.chmod(script_dst, rwxr_xr_x)

                from common.tools import log_check_call
		log_check_call(['/usr/sbin/chroot', info.root, 'dpkg', '-i', '/tmp/one-context_3.8.1.deb'])
		# Fix start
                from common.tools import sed_i
                vmcontext_def = os.path.join(info.root, 'etc/init.d/vmcontext')
                sed_i(vmcontext_def, '# Default-Start:', '# Default-Start: 2 3 4 5')
		os.chmod(vmcontext_def, rwxr_xr_x)
		log_check_call(['/usr/sbin/chroot', info.root, 'update-rc.d', 'vmcontext', 'start', '90', '2', '3', '4', '5', 'stop', '90', '0', '6'])

		# Load all pubkeys in root authorized_keys
                script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets/one-pubkey.sh'))
                script_dst = os.path.join(info.root, 'etc/one-context.d/one-pubkey.sh')
                copy(script_src, script_dst)

                # If USER_EC2_DATA is a script, execute it
                script_src = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets/one-ec2.sh'))
                script_dst = os.path.join(info.root, 'etc/one-context.d/one-ec2.sh')
                copy(script_src, script_dst)

