from bootstrapvz.base import Task
from bootstrapvz.common import phases
import volume
import workspace


class Create(Task):
    description = 'Creating volume folder'
    phase = phases.volume_creation
    successors = [volume.Attach]

    @classmethod
    def run(cls, info):
        import os.path
        info.root = os.path.join(info.workspace, 'root')
        info.volume.create(info.root)


class Delete(Task):
    description = 'Deleting volume folder'
    phase = phases.cleaning
    successors = [workspace.DeleteWorkspace]

    @classmethod
    def run(cls, info):
        info.volume.delete()
        del info.root
