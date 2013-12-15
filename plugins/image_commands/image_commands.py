from base import Task
from common import phases
from plugins.user_packages.user_packages import AddUserPackages, \
                                                AddLocalUserPackages


class ImageExecuteCommand(Task):
    description = 'Execute command in the image'
    phase = phases.system_modification
    predecessors = [AddUserPackages, AddLocalUserPackages]

    def run(self, info):
        from common.tools import log_check_call
        for user_cmd in info.manifest.plugins['image_commands']['commands']:
            command = []
            for elt in user_cmd:
                fragment = elt.format(root=info.root)
                command.append(fragment)
            log_check_call(command)
