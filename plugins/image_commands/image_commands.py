from base import Task
from common import phases
import os
from common.tasks.packages import ImagePackages
from common.tasks.host import CheckPackages
from common.tasks.filesystem import MountVolume


class ImageExecuteCommand(Task):
    description = 'Execute command in the image'
    phase = phases.system_modification

    def run(self, info):
        from common.tools import log_check_call

        for user_cmd in info.manifest.plugins['image_commands']['commands']:
            command = []
            for elt in user_cmd:
                fragment = elt.format(
                                root=info.root,
                                image=info.loopback_file,
                                filesystem=info.manifest.volume['filesystem'])
                command.append(fragment) 
            log_check_call(command)


