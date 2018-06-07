from . import tasks


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.update([tasks.AddPackages,
                    tasks.AddRequiredCommands,
                    tasks.CheckPlaybookPath,
                    tasks.RunAnsiblePlaybook,
                    ])
