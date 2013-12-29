import tasks


def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def resolve_tasks(tasklist, manifest):
	from common.tasks import security
	from common.tasks import loopback
	tasklist.remove(security.DisableSSHPasswordAuthentication,
	                loopback.MoveImage,
	                )
	from common.tasks import volume
	tasklist.add(tasks.CreateVagrantBoxDir,
	             tasks.AddPackages,
	             tasks.AddInsecurePublicKey,
	             tasks.PackageBox,
	             tasks.RemoveVagrantBoxDir,
	             volume.Delete,
	             )


def resolve_rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter)

	counter_task(tasks.CreateVagrantBoxDir, tasks.RemoveVagrantBoxDir)
