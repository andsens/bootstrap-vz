from bootstrapvz.base import Task
from bootstrapvz.common import phases


class ImageExecuteCommand(Task):
    description = 'Executing commands in the image'
    phase = phases.user_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        for raw_command in info.manifest.plugins['commands']['commands']:
            command = map(lambda part: part.format(root=info.root, **info.manifest_vars), raw_command)
            shell = len(command) == 1
            log_check_call(command, shell=shell)
