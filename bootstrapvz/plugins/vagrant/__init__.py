import tasks


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	from bootstrapvz.common import task_groups
	from bootstrapvz.common.tasks import ssh
	taskset.update(task_groups.ssh_group)
	taskset.discard(ssh.DisableSSHPasswordAuthentication)

	from bootstrapvz.common.tasks import loopback
	taskset.discard(loopback.MoveImage)

	from bootstrapvz.common.tasks import volume
	taskset.update([tasks.CheckBoxPath,
	                tasks.CreateVagrantBoxDir,
	                tasks.AddPackages,
	                tasks.CreateVagrantUser,
	                tasks.PasswordlessSudo,
	                tasks.SetRootPassword,
	                tasks.AddInsecurePublicKey,
	                tasks.PackageBox,
	                tasks.RemoveVagrantBoxDir,
	                volume.Delete,
	                ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	counter_task(taskset, tasks.CreateVagrantBoxDir, tasks.RemoveVagrantBoxDir)
