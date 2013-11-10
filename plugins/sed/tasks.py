from base import Task
from common import phases
from common.tasks.apt import AptUpgrade
from common.tools import sed_i
import os


class DoSeds(Task):
        description = 'Sedding files'
        phase = phases.system_modification
	after = [AptUpgrade]
        def run(self, info):

			chroot_path = os.path.join(info.root, info.manifest.plugins['sed']['file'])
			sed_i(chroot_path, info.manifest.plugins['sed']['find'], info.manifest.plugins['sed']['replace'])
