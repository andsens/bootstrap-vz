from tasks import Snapshot
from tasks import CopyImage
from tasks import CreateFromSnapshot
from tasks import CreateFromImage
from providers.ec2.tasks import ebs
from common.tasks import loopback
from common.tasks import bootstrap
from common.tasks import filesystem
from common.tasks import parted


def tasks(tasklist, manifest):
	settings = manifest.plugins['prebootstrapped']
	if manifest.volume['backing'] == 'ebs':
		if 'snapshot' in settings and settings['snapshot'] is not None:
			tasklist.replace(ebs.Create, CreateFromSnapshot())
			tasklist.remove(filesystem.FormatVolume,
			                filesystem.TuneVolumeFS,
			                filesystem.AddXFSProgs,
			                bootstrap.MakeTarball,
			                bootstrap.Bootstrap)
		else:
			tasklist.add(Snapshot())
	else:
		if 'image' in settings and settings['image'] is not None:
			tasklist.add(CreateFromImage())
			tasklist.remove(loopback.Create,
			                loopback.CreateQemuImg,
			                parted.PartitionVolume,
			                parted.FormatPartitions,
			                filesystem.FormatVolume,
			                filesystem.TuneVolumeFS,
			                filesystem.AddXFSProgs,
			                bootstrap.MakeTarball,
			                bootstrap.Bootstrap)
		else:
			tasklist.add(CopyImage())


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter())

	if manifest.volume['backing'] == 'ebs':
		counter_task(CreateFromSnapshot, ebs.Delete)
	else:
		counter_task(CreateFromImage, loopback.Delete)


def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)
