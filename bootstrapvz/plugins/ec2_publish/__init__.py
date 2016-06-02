def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	import tasks
	taskset.add(tasks.CopyAmiToRegions)
	if 'manifest_url' in manifest.plugins['ec2_publish']:
		taskset.add(tasks.PublishAmiManifest)

	ami_public = manifest.plugins['ec2_publish'].get('public')
	if ami_public:
		taskset.add(tasks.PublishAmi)
