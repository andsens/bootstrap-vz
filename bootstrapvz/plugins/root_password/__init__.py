

def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    from bootstrapvz.common.tasks import ssh
    from tasks import SetRootPassword
    taskset.discard(ssh.DisableSSHPasswordAuthentication)
    taskset.add(ssh.EnableRootLogin)
    taskset.add(SetRootPassword)
