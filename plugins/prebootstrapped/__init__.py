from tasks import CreateSnapshot
from tasks import CreateVolumeFromSnapshot
from providers.ec2.tasks import ebs


def tasks(tasklist, manifest):
	from providers.ec2.tasks import bootstrap
	from providers.ec2.tasks import filesystem
	if manifest.plugins['prebootstrapped']['snapshot'] == "":
		tasklist.add(CreateSnapshot())
	else:
		tasklist.replace(ebs.CreateVolume, CreateVolumeFromSnapshot())
		tasklist.remove(filesystem.FormatVolume,
		                filesystem.TuneVolumeFS,
		                filesystem.AddXFSProgs,
		                bootstrap.MakeTarball,
		                bootstrap.Bootstrap)


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter())

	counter_task(CreateVolumeFromSnapshot, ebs.DeleteVolume)


def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)
