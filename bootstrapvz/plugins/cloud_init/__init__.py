

def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    import tasks
    import bootstrapvz.providers.ec2.tasks.initd as initd_ec2
    from bootstrapvz.common.tasks import apt
    from bootstrapvz.common.tasks import initd
    from bootstrapvz.common.tasks import ssh

    from bootstrapvz.common.releases import wheezy
    if manifest.release == wheezy:
        taskset.add(apt.AddBackports)

    taskset.update([tasks.SetMetadataSource,
                    tasks.AddCloudInitPackages,
                    ])

    options = manifest.plugins['cloud_init']
    if 'username' in options:
        taskset.add(tasks.SetUsername)
    if 'groups' in options and len(options['groups']):
        taskset.add(tasks.SetGroups)
    if 'enable_modules' in options:
        taskset.add(tasks.EnableModules)
    if 'disable_modules' in options:
        taskset.add(tasks.DisableModules)

    taskset.discard(initd_ec2.AddEC2InitScripts)
    taskset.discard(initd.AddExpandRoot)
    taskset.discard(initd.AdjustExpandRootScript)
    taskset.discard(initd.AdjustGrowpartWorkaround)
    taskset.discard(ssh.AddSSHKeyGeneration)
