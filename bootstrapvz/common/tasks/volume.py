from bootstrapvz.base import Task
from .. import phases
import workspace


class Attach(Task):
    description = 'Attaching the volume'
    phase = phases.volume_creation

    @classmethod
    def run(cls, info):
        info.volume.attach()


class Detach(Task):
    description = 'Detaching the volume'
    phase = phases.volume_unmounting

    @classmethod
    def run(cls, info):
        info.volume.detach()


class Delete(Task):
    description = 'Deleting the volume'
    phase = phases.cleaning
    successors = [workspace.DeleteWorkspace]

    @classmethod
    def run(cls, info):
        info.volume.delete()
