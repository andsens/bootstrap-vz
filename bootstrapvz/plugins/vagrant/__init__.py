import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	from bootstrapvz.common.tasks import security
	from bootstrapvz.common.tasks import loopback
	from bootstrapvz.common.tasks import network
	taskset.discard(security.DisableSSHPasswordAuthentication)
	taskset.discard(loopback.MoveImage)
	taskset.discard(network.RemoveHostname)

	from bootstrapvz.common.tasks import volume
	taskset.update([tasks.CheckBoxPath,
	                tasks.CreateVagrantBoxDir,
	                tasks.AddPackages,
	                tasks.SetHostname,
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
