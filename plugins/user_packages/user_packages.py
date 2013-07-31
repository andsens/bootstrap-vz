from base import Task
from common import phases
import os
from providers.one.tasks.packages import ImagePackages
from providers.one.tasks.host import CheckPackages
from providers.one.tasks.filesystem import MountVolume


class AddUserPackages(Task):
	description = 'Adding user defined packages to the image packages'
	phase = phases.preparation
	after = [ImagePackages]
	before = [CheckPackages]

	def run(self, info):
		if 'repo' not in info.manifest.plugins['user_packages']:
			return
		for pkg in info.manifest.plugins['user_packages']['repo']:
			info.img_packages[0].add(pkg)

class AddLocalUserPackages(Task):
        description = 'Adding user local packages to the image packages'
        phase = phases.system_modification
        after = [MountVolume]

        def run(self, info):
                if 'local' not in info.manifest.plugins['user_packages']:
                        return

                import stat
                rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                             stat.S_IRGRP                | stat.S_IXGRP |
                             stat.S_IROTH                | stat.S_IXOTH)

                from shutil import copy
                from common.tools import log_check_call

		for pkg in info.manifest.plugins['user_packages']['local']:
                	script_src = os.path.normpath(pkg)
                	script_dst = os.path.join(info.root, 'tmp/'+os.path.basename(script_src))
                	copy(script_src, script_dst)
                	os.chmod(script_dst, rwxr_xr_x)

                	log_check_call(['/usr/sbin/chroot', info.root, 'dpkg', '-i', '/tmp/'+os.path.basename(script_src)])

