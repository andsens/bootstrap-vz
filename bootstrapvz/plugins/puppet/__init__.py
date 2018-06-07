from . import tasks


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.add(tasks.CheckRequestedDebianRelease)
    taskset.add(tasks.AddPuppetlabsPC1SourcesList)
    taskset.add(tasks.InstallPuppetlabsPC1ReleaseKey)
    taskset.add(tasks.InstallPuppetAgent)
    if 'assets' in manifest.plugins['puppet']:
        taskset.add(tasks.CheckAssetsPath)
        taskset.add(tasks.CopyPuppetAssets)
    if 'manifest' in manifest.plugins['puppet']:
        taskset.add(tasks.CheckManifestPath)
        taskset.add(tasks.ApplyPuppetManifest)
    if 'install_modules' in manifest.plugins['puppet']:
        taskset.add(tasks.InstallModules)
    if manifest.plugins['puppet'].get('enable_agent', False):
        taskset.add(tasks.EnableAgent)
