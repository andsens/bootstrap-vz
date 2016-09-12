def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    import tasks
    taskset.add(tasks.CopyAmiToRegions)
    if 'manifest_url' in manifest.plugins['ec2_publish']:
        taskset.add(tasks.PublishAmiManifest)

    ami_public = manifest.plugins['ec2_publish'].get('public')
    if ami_public:
        taskset.add(tasks.PublishAmi)
