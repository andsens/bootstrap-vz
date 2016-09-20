import tasks


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path

    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    if ('mkdirs' in manifest.plugins['file_copy']):
        taskset.add(tasks.MkdirCommand)
    if ('files' in manifest.plugins['file_copy']):
        taskset.add(tasks.ValidateFiles)
        taskset.add(tasks.FileCopyCommand)
