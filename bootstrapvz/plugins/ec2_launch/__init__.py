def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    import tasks
    taskset.add(tasks.LaunchEC2Instance)
    if 'print_public_ip' in manifest.plugins['ec2_launch']:
        taskset.add(tasks.PrintPublicIPAddress)
    if manifest.plugins['ec2_launch'].get('deregister_ami', False):
        taskset.add(tasks.DeregisterAMI)
