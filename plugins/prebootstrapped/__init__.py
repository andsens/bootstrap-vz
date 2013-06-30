from tasks import CreateVolumeFromSnapshot
from providers.ec2.tasks import ebs


def tasks(tasklist, manifest):
	from providers.ec2.tasks import bootstrap
	from providers.ec2.tasks import filesystem
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

	counter_task(ebs.CreateVolumeFromSnapshot, ebs.DeleteVolume)
