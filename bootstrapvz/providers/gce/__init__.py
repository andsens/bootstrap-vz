import tasks.apt
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.host
import tasks.packages
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import security
from bootstrapvz.common.tasks import initd
import bootstrapvz.plugins.cloud_init.tasks


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(tasklist, manifest):
	tasklist.update(bootstrapvz.common.task_groups.get_standard_groups(manifest))

	tasklist.update([bootstrapvz.plugins.cloud_init.tasks.AddBackports,
	                 loopback.Create,
	                 tasks.apt.SetPackageRepositories,
	                 tasks.apt.ImportGoogleKey,
	                 tasks.packages.DefaultPackages,
	                 tasks.packages.GooglePackages,
	                 tasks.packages.InstallGSUtil,

	                 tasks.configuration.GatherReleaseInformation,

	                 security.EnableShadowConfig,
	                 tasks.host.DisableIPv6,
	                 tasks.boot.ConfigureGrub,
	                 initd.AddSSHKeyGeneration,
	                 tasks.apt.CleanGoogleRepositoriesAndKeys,

	                 loopback.MoveImage,
	                 tasks.image.CreateTarball,
	                 ])

	if 'gcs_destination' in manifest.image:
		tasklist.add(tasks.image.UploadImage)
		if 'gce_project' in manifest.image:
			tasklist.add(tasks.image.RegisterImage)


def resolve_rollback_tasks(tasklist, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
