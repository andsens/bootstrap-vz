from . import tasks
from bootstrapvz.common.tools import rel_path


def validate_manifest(data, validator, error):
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.add(tasks.InstallGrowpart)
    taskset.add(tasks.InstallExpandRootScripts)
