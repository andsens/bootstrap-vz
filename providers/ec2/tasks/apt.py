from base import Task
from common import phases
from common.tools import log_check_call
import os
from config import AptSources


class AptUpgrade(Task):
	description = 'Upgrading packages and fixing broken dependencies'
	phase = phases.system_modification
	after = [AptSources]

	def run(self, info):
		rc_policy_path = os.path.join(info.root, 'usr/sbin/policy-rc.d')
		with open(rc_policy_path, 'w') as rc_policy:
			rc_policy.write('#!/bin/sh\nexit 101')
		import stat
		os.chmod(rc_policy_path,
		         stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		         stat.S_IRGRP                | stat.S_IXGRP |
		         stat.S_IROTH                | stat.S_IXOTH)
		log_check_call(['chroot', info.root, 'apt-get', 'update'])
		log_check_call(['chroot', info.root, 'apt-get', '-f', '-y', 'install'])
		log_check_call(['chroot', info.root, 'apt-get', '-y', 'upgrade'])
