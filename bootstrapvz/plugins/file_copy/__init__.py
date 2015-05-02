import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	taskset.add(tasks.ValidateSourcePaths)

	if ('mkdirs' in manifest.plugins['file_copy']):
		taskset.add(tasks.MkdirCommand)
	if ('files' in manifest.plugins['file_copy']):
		taskset.add(tasks.FileCopyCommand)
