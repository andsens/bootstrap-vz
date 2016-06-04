from bootstrapvz.base import Task
from .. import phases


class CreateWorkspace(Task):
    description = 'Creating workspace'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        import os
        os.makedirs(info.workspace)


class DeleteWorkspace(Task):
    description = 'Deleting workspace'
    phase = phases.cleaning

    @classmethod
    def run(cls, info):
        import os
        os.rmdir(info.workspace)
