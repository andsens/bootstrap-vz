import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.join(os.path.dirname(__file__), 'manifest-schema.json')
	validator(data, schema_path)
	if 'zerofree' in data['plugins']['minimize_size']:
		zerofree_schema_path = os.path.join(os.path.dirname(__file__), 'manifest-schema-zerofree.json')
		validator(data, zerofree_schema_path)
	if data['plugins']['minimize_size'].get('shrink', False) and data['volume']['backing'] != 'vmdk':
		error('Can only shrink vmdk images', ['plugins', 'minimize_size', 'shrink'])


def resolve_tasks(taskset, manifest):
	taskset.update([tasks.AddFolderMounts,
	                tasks.RemoveFolderMounts,
	                ])
	if 'zerofree' in manifest.plugins['minimize_size']:
		taskset.add(tasks.CheckZerofreePath)
		taskset.add(tasks.Zerofree)
	if manifest.plugins['minimize_size'].get('shrink', False):
		taskset.add(tasks.CheckVMWareDMCommand)
		taskset.add(tasks.ShrinkVolume)


def resolve_rollback_tasks(taskset, manifest, counter_task):
	counter_task(tasks.AddFolderMounts, tasks.RemoveFolderMounts)
