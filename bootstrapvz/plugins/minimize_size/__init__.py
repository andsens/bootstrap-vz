import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.join(os.path.dirname(__file__), 'manifest-schema.yml')
	validator(data, schema_path)
	if data['plugins']['minimize_size'].get('shrink', False) and data['volume']['backing'] != 'vmdk':
		error('Can only shrink vmdk images', ['plugins', 'minimize_size', 'shrink'])


def resolve_tasks(taskset, manifest):
	taskset.update([tasks.AddFolderMounts,
	                tasks.RemoveFolderMounts,
	                ])
	if manifest.plugins['minimize_size'].get('zerofree', False):
		taskset.add(tasks.AddRequiredCommands)
		taskset.add(tasks.Zerofree)
	if manifest.plugins['minimize_size'].get('shrink', False):
		taskset.add(tasks.AddRequiredCommands)
		taskset.add(tasks.ShrinkVolume)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	counter_task(taskset, tasks.AddFolderMounts, tasks.RemoveFolderMounts)
