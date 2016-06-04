from bootstrapvz.base import Task
from .. import phases


class TriggerRollback(Task):
    phase = phases.cleaning

    description = 'Triggering a rollback by throwing an exception'

    @classmethod
    def run(cls, info):
        from ..exceptions import TaskError
        raise TaskError('Trigger rollback')
