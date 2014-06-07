from bootstrapvz.common import task_groups
import tasks.apt
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.host
import tasks.packages
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import ssh
from bootstrapvz.common.tasks import volume
import bootstrapvz.plugins.cloud_init.tasks


def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	taskset.update(task_groups.get_standard_groups(manifest))

	taskset.update([bootstrapvz.plugins.cloud_init.tasks.AddBackports,
	                loopback.AddRequiredCommands,
	                loopback.Create,
	                tasks.apt.SetPackageRepositories,
	                tasks.apt.ImportGoogleKey,
	                tasks.packages.DefaultPackages,
	                tasks.packages.GooglePackages,
	                tasks.packages.InstallGSUtil,

	                tasks.configuration.GatherReleaseInformation,

	                tasks.host.DisableIPv6,
	                tasks.boot.ConfigureGrub,
	                initd.InstallInitScripts,
	                ssh.AddSSHKeyGeneration,
	                tasks.apt.CleanGoogleRepositoriesAndKeys,

	                loopback.MoveImage,
	                tasks.image.CreateTarball,
	                volume.Delete,
	                ])

	if 'gcs_destination' in manifest.image:
		taskset.add(tasks.image.UploadImage)
		if 'gce_project' in manifest.image:
			taskset.add(tasks.image.RegisterImage)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	taskset.update(task_groups.get_standard_rollback_tasks(completed))
