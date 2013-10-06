from tasks import Snapshot
from tasks import CopyImage
from tasks import CreateFromSnapshot
from tasks import CreateFromImage
from tasks import SetBootMountDir
from providers.ec2.tasks import ebs
from common.tasks import loopback
from common.tasks import volume
from common.tasks import bootstrap
from common.tasks import filesystem
from common.tasks import partitioning


def tasks(tasklist, manifest):
	settings = manifest.plugins['prebootstrapped']
	skip_tasks = [filesystem.Format,
	              partitioning.PartitionVolume,
	              filesystem.TuneVolumeFS,
	              filesystem.AddXFSProgs,
	              filesystem.CreateBootMountDir,
	              bootstrap.MakeTarball,
	              bootstrap.Bootstrap]
	if manifest.volume['backing'] == 'ebs':
		if 'snapshot' in settings and settings['snapshot'] is not None:
			tasklist.replace(ebs.Create, CreateFromSnapshot)
			tasklist.remove(*skip_tasks)
			if 'boot' in manifest.volume['partitions']:
				tasklist.add(SetBootMountDir)
		else:
			tasklist.add(Snapshot)
	else:
		if 'image' in settings and settings['image'] is not None:
			tasklist.replace(loopback.Create, CreateFromImage)
			tasklist.remove(*skip_tasks)
			if 'boot' in manifest.volume['partitions']:
				tasklist.add(SetBootMountDir)
		else:
			tasklist.add(CopyImage)


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter)

	if manifest.volume['backing'] == 'ebs':
		counter_task(CreateFromSnapshot, volume.Delete)
	else:
		counter_task(CreateFromImage, volume.Delete)


def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)
