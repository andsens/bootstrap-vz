import tasks


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.add(tasks.AddPackages)
    taskset.add(tasks.CheckPlaybookPath)
    taskset.add(tasks.RunAnsiblePlaybook)
