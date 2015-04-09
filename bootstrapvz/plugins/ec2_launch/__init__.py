def validate_manifest(data, validator, error):
    import os.path
    schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
    validator(data, schema_path)


def resolve_tasks(taskset, manifest):
    import tasks
    taskset.add(tasks.LaunchEC2Instance)
    if 'print_public_ip' in manifest.plugins['ec2_launch']:
        taskset.add(tasks.PrintPublicIPAddress)
    if manifest.plugins['ec2_launch'].get('deregister_ami', False):
        taskset.add(tasks.DeregisterAMI)
