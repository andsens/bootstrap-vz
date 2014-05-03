import tasks.packages
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import security
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import workspace


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)

	if data['volume']['partitions']['type'] == 'none' and data['system']['bootloader'] != 'extlinux':
			error('Only extlinux can boot from unpartitioned disks', ['system', 'bootloader'])


def resolve_tasks(taskset, manifest):
	from bootstrapvz.common import task_groups
	taskset.update(task_groups.get_standard_groups(manifest))

	taskset.update([tasks.packages.DefaultPackages,
	                loopback.Create,
	                security.EnableShadowConfig,
	                initd.InstallInitScripts,
	                loopback.MoveImage,
	                ])

	if manifest.bootstrapper.get('guest_additions', False):
		from tasks import guest_additions
		taskset.update([guest_additions.CheckGuestAdditionsPath,
		                guest_additions.AddGuestAdditionsPackages,
		                guest_additions.InstallGuestAdditions,
		                ])


def resolve_rollback_tasks(taskset, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
