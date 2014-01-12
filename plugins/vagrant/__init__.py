import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	from common.tasks import security
	from common.tasks import loopback
	taskset.discard(security.DisableSSHPasswordAuthentication)
	taskset.discard(loopback.MoveImage)

	from common.tasks import volume
	taskset.update([tasks.CreateVagrantBoxDir,
	                tasks.AddPackages,
	                tasks.CreateVagrantUser,
	                tasks.PasswordlessSudo,
	                tasks.SetRootPassword,
	                tasks.AddInsecurePublicKey,
	                tasks.PackageBox,
	                tasks.RemoveVagrantBoxDir,
	                volume.Delete,
	                ])


def resolve_rollback_tasks(taskset, manifest, counter_task):
	counter_task(tasks.CreateVagrantBoxDir, tasks.RemoveVagrantBoxDir)
