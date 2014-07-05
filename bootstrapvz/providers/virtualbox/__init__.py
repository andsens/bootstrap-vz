from bootstrapvz.common import task_groups
import tasks.packages
from bootstrapvz.common.tasks import loopback


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	taskset.update(task_groups.get_standard_groups(manifest))

	taskset.update([tasks.packages.DefaultPackages,
	                loopback.AddRequiredCommands,
	                loopback.Create,
	                loopback.MoveImage,
	                ])

	if manifest.provider.get('guest_additions', False):
		from tasks import guest_additions
		taskset.update([guest_additions.CheckGuestAdditionsPath,
		                guest_additions.AddGuestAdditionsPackages,
		                guest_additions.InstallGuestAdditions,
		                ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	taskset.update(task_groups.get_standard_rollback_tasks(completed))
