import tasks


def validate_manifest(data, validator, error):
	import os.path

	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)

	for i, file_entry in enumerate(data['plugins']['file_copy']['files']):
		srcfile = file_entry['src']
		if not os.path.isfile(srcfile):
			msg = 'The source file %s does not exist.' % srcfile
			error(msg, ['plugins', 'file_copy', 'files', i])


def resolve_tasks(taskset, manifest):
	if ('mkdirs' in manifest.plugins['file_copy']):
		taskset.add(tasks.MkdirCommand)
	if ('files' in manifest.plugins['file_copy']):
		taskset.add(tasks.FileCopyCommand)
