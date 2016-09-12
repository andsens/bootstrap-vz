from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import host


class AddRequiredCommands(Task):
    description = 'Adding commands required for docker'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        info.host_dependencies['docker'] = 'docker.io'
