def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import log_check_call
    import os.path
    schema_path = os.path.join(os.path.dirname(__file__),
                               'schema.yaml')
    validator(data, schema_path)
    log_check_call(['debconf-set-selections', '--checkonly'],
                   stdin=data['plugins']['debconf'])


def resolve_tasks(taskset, manifest):
    import tasks
    taskset.update([tasks.DebconfSetSelections])
