import tasks.apt
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.host
import tasks.packages
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import security
from bootstrapvz.common.tasks import network
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import workspace


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(tasklist, manifest):
	import bootstrapvz.common.task_groups
	tasklist.update(bootstrapvz.common.task_groups.base_set)
	tasklist.update(bootstrapvz.common.task_groups.volume_set)
	tasklist.update(bootstrapvz.common.task_groups.mounting_set)
	tasklist.update(bootstrapvz.common.task_groups.get_apt_set(manifest))
	tasklist.update(bootstrapvz.common.task_groups.locale_set)

	tasklist.update(bootstrapvz.common.task_groups.bootloader_set.get(manifest.system['bootloader']))

	if manifest.volume['partitions']['type'] != 'none':
		tasklist.update(bootstrapvz.common.task_groups.partitioning_set)

	tasklist.update([bootstrapvz.plugins.cloud_init.tasks.AddBackports,
	                 loopback.Create,
	                 tasks.apt.SetPackageRepositories,
	                 tasks.apt.ImportGoogleKey,
	                 tasks.packages.DefaultPackages,
	                 tasks.packages.GooglePackages,
	                 tasks.packages.InstallGSUtil,

	                 tasks.configuration.GatherReleaseInformation,

	                 security.EnableShadowConfig,
	                 network.RemoveDNSInfo,
	                 network.RemoveHostname,
	                 network.ConfigureNetworkIF,
	                 tasks.host.DisableIPv6,
	                 tasks.host.SetHostname,
	                 tasks.boot.ConfigureGrub,
	                 initd.AddSSHKeyGeneration,
	                 initd.InstallInitScripts,
	                 tasks.apt.CleanGoogleRepositoriesAndKeys,

	                 loopback.MoveImage,
	                 tasks.image.CreateTarball,
	                 ])

	if 'gcs_destination' in manifest.image:
		tasklist.add(tasks.image.UploadImage)
		if 'gce_project' in manifest.image:
			tasklist.add(tasks.image.RegisterImage)

	tasklist.update(bootstrapvz.common.task_groups.get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		tasklist.update(bootstrapvz.common.task_groups.boot_partition_set)


def resolve_rollback_tasks(tasklist, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
