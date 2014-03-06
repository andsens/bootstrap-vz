import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	taskset.add(tasks.AddPackages)
	if 'assets' in manifest.plugins['puppet']:
		taskset.add(tasks.CheckAssetsPath)
		taskset.add(tasks.CopyPuppetAssets)
	if 'manifest' in manifest.plugins['puppet']:
		taskset.add(tasks.CheckManifestPath)
		taskset.add(tasks.ApplyPuppetManifest)
