def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    import tasks
    taskset.add(tasks.CheckAptProxy)
    taskset.add(tasks.SetAptProxy)
    if not manifest.plugins['apt_proxy'].get('persistent', False):
        taskset.add(tasks.RemoveAptProxy)
