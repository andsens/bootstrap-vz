from bootstrapvz.common.tools import rel_path
import tasks
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.releases import wheezy


def validate_manifest(data, validator, error):
    validator(data, rel_path(__file__, 'manifest-schema.yml'))

    from bootstrapvz.common.releases import get_release
    if get_release(data['system']['release']) == wheezy:
        # prefs is a generator of apt preferences across files in the manifest
        prefs = (item for vals in data.get('packages', {}).get('preferences', {}).values() for item in vals)
        if not any('linux-image' in item['package'] and 'wheezy-backports' in item['pin'] for item in prefs):
            msg = 'The backports kernel is required for the docker daemon to function properly'
            error(msg, ['packages', 'preferences'])


def resolve_tasks(taskset, manifest):
    if manifest.release == wheezy:
        taskset.add(apt.AddBackports)
    taskset.add(tasks.AddDockerDeps)
    taskset.add(tasks.AddDockerBinary)
    taskset.add(tasks.AddDockerInit)
    taskset.add(tasks.EnableMemoryCgroup)
    if len(manifest.plugins['docker_daemon'].get('pull_images', [])) > 0:
        taskset.add(tasks.PullDockerImages)
