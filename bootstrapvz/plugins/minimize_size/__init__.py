import tasks.mounts
import tasks.shrink
import tasks.apt
import tasks.dpkg


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.join(os.path.dirname(__file__), 'manifest-schema.yml')
	validator(data, schema_path)
	if data['plugins']['minimize_size'].get('shrink', False) and data['volume']['backing'] != 'vmdk':
		error('Can only shrink vmdk images', ['plugins', 'minimize_size', 'shrink'])


def resolve_tasks(taskset, manifest):
	taskset.update([tasks.mounts.AddFolderMounts,
	                tasks.mounts.RemoveFolderMounts,
	                ])
	if manifest.plugins['minimize_size'].get('zerofree', False):
		taskset.add(tasks.shrink.AddRequiredCommands)
		taskset.add(tasks.shrink.Zerofree)
	if manifest.plugins['minimize_size'].get('shrink', False):
		taskset.add(tasks.shrink.AddRequiredCommands)
		taskset.add(tasks.shrink.ShrinkVolume)
	if 'apt' in manifest.plugins['minimize_size']:
		apt = manifest.plugins['minimize_size']['apt']
		if apt.get('autoclean', False):
			taskset.add(tasks.apt.AutomateAptClean)
		if 'languages' in apt:
			taskset.add(tasks.apt.FilterTranslationFiles)
		if apt.get('gzip_indexes', False):
			taskset.add(tasks.apt.AptGzipIndexes)
		if apt.get('autoremove_suggests', False):
			taskset.add(tasks.apt.AptAutoremoveSuggests)
		if 'locales' in apt:
			taskset.update([tasks.dpkg.CreateBootstrapFilterScripts,
			                tasks.dpkg.DeleteBootstrapFilterScripts,
			                tasks.dpkg.FilterLocales,
			                ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	counter_task(taskset, tasks.AddFolderMounts, tasks.RemoveFolderMounts)
	counter_task(taskset, tasks.CreateBootstrapFilterScripts, tasks.DeleteBootstrapFilterScripts)
