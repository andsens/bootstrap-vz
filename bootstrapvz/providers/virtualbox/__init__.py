import tasks.packages
from common.tasks import volume
from common.tasks import loopback
from common.tasks import partitioning
from common.tasks import filesystem
from common.tasks import bootstrap
from common.tasks import security
from common.tasks import network
from common.tasks import initd
from common.tasks import cleanup
from common.tasks import workspace


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)

	if data['volume']['partitions']['type'] == 'none' and data['system']['bootloader'] != 'extlinux':
			error('Only extlinux can boot from unpartitioned disks', ['system', 'bootloader'])


def resolve_tasks(taskset, manifest):
	import common.task_sets
	taskset.update(common.task_sets.base_set)
	taskset.update(common.task_sets.volume_set)
	taskset.update(common.task_sets.mounting_set)
	taskset.update(common.task_sets.get_apt_set(manifest))
	taskset.update(common.task_sets.locale_set)

	taskset.update(common.task_sets.bootloader_set.get(manifest.system['bootloader']))

	if manifest.volume['partitions']['type'] != 'none':
		taskset.update(common.task_sets.partitioning_set)

	taskset.update([tasks.packages.DefaultPackages,

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

	if manifest.bootstrapper.get('guest_additions', False):
		from tasks import guest_additions
		taskset.update([guest_additions.CheckGuestAdditionsPath,
		                guest_additions.AddGuestAdditionsPackages,
		                guest_additions.InstallGuestAdditions,
		                ])

	if manifest.bootstrapper.get('tarball', False):
		taskset.add(bootstrap.MakeTarball)

	taskset.update(common.task_sets.get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		taskset.update(common.task_sets.boot_partition_set)


def resolve_rollback_tasks(taskset, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
