import tasks
import os.path
from bootstrapvz.common.exceptions import ManifestError


def validate_manifest(data, validator, error):
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	try:
		validator(data, schema_path)
	except ManifestError, e:
		error('docker_daemon manifest validation failed: "%s"' % e.message, e.json_path)
	if data.get('system', {}).get('release', None) in ['wheezy', 'stable']:
		# prefs is a generator of apt preferences across files in the manifest
		prefs = (item for vals in data.get('packages', {}).get('preferences', {}).values() for item in vals)
		if not any('linux-image' in item['package'] and 'wheezy-backports' in item['pin'] for item in prefs):
			msg = 'The backports kernel is required for the docker daemon to function properly'
			error(msg, ['packages', 'preferences'])


def resolve_tasks(taskset, manifest):
	taskset.add(tasks.AddDockerDeps)
	taskset.add(tasks.AddDockerBinary)
	taskset.add(tasks.AddDockerInit)
