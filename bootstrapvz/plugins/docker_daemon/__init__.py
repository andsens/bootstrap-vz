import os.path
import tasks
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tools import get_codename


def validate_manifest(data, validator, error):
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)
	if get_codename(data['system']['release']) == 'wheezy':
		# prefs is a generator of apt preferences across files in the manifest
		prefs = (item for vals in data.get('packages', {}).get('preferences', {}).values() for item in vals)
		if not any('linux-image' in item['package'] and 'wheezy-backports' in item['pin'] for item in prefs):
			msg = 'The backports kernel is required for the docker daemon to function properly'
			error(msg, ['packages', 'preferences'])


def resolve_tasks(taskset, manifest):
	if get_codename(manifest.system['release']) == 'wheezy':
		taskset.add(apt.AddBackports)
	taskset.add(tasks.AddDockerDeps)
	taskset.add(tasks.AddDockerBinary)
	taskset.add(tasks.AddDockerInit)
	taskset.add(tasks.EnableMemoryCgroup)
        if len(manifest.plugins['docker_daemon'].get('pull_images', [])) > 0:
                taskset.add(tasks.PullDockerImages)
