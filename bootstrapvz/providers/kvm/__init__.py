import tasks.packages
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import bootstrap
from bootstrapvz.common.tasks import security
from bootstrapvz.common.tasks import network
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import cleanup
from bootstrapvz.common.tasks import workspace


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)

	if data['volume']['partitions']['type'] == 'none' and data['system']['bootloader'] != 'extlinux':
			error('Only extlinux can boot from unpartitioned disks', ['system', 'bootloader'])


def resolve_tasks(tasklist, manifest):
	from bootstrapvz.common import task_sets
	tasklist.update(task_sets.base_set)
	tasklist.update(task_sets.volume_set)
	tasklist.update(task_sets.mounting_set)
	tasklist.update(task_sets.get_apt_set(manifest))
	tasklist.update(task_sets.locale_set)

	tasklist.update(task_sets.bootloader_set.get(manifest.system['bootloader']))

	if manifest.volume['partitions']['type'] != 'none':
		tasklist.update(task_sets.partitioning_set)

	tasklist.update([tasks.packages.DefaultPackages,

	                 loopback.Create,

	                 security.EnableShadowConfig,
	                 network.RemoveDNSInfo,
	                 network.ConfigureNetworkIF,
	                 network.RemoveHostname,
	                 initd.AddSSHKeyGeneration,
	                 initd.InstallInitScripts,
	                 cleanup.ClearMOTD,
	                 cleanup.CleanTMP,

	                 loopback.MoveImage,
	                 ])

	if manifest.bootstrapper.get('tarball', False):
		tasklist.add(bootstrap.MakeTarball)

	if manifest.bootstrapper.get('virtio', []):
		from tasks import virtio
		tasklist.update([virtio.VirtIO])

	tasklist.update(task_sets.get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		tasklist.update(task_sets.boot_partition_set)


def resolve_rollback_tasks(tasklist, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
