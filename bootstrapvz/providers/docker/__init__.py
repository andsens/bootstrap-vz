from bootstrapvz.common.tasks import folder
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common import task_groups
import tasks.commands
import tasks.image


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	taskset.update(task_groups.get_base_group(manifest))
	taskset.update([folder.Create,
	                filesystem.CopyMountTable,
	                filesystem.RemoveMountTable,
	                folder.Delete,
	                ])
	taskset.update(task_groups.get_network_group(manifest))
	taskset.update(task_groups.get_apt_group(manifest))
	taskset.update(task_groups.get_locale_group(manifest))
	taskset.update(task_groups.security_group)
	taskset.update(task_groups.cleanup_group)

	taskset.update([tasks.commands.AddRequiredCommands,
	                tasks.image.CreateDockerfileEntry,
	                tasks.image.CreateImage,
	                ])
	if 'labels' in manifest.provider:
		taskset.add(tasks.image.PopulateLabels)
	if 'dockerfile' in manifest.provider:
		taskset.add(tasks.image.AppendManifestDockerfile)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	taskset.update(task_groups.get_standard_rollback_tasks(completed))
