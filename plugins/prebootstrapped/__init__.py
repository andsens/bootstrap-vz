from tasks import Snapshot
from tasks import CopyImage
from tasks import CreateFromSnapshot
from tasks import CreateFromImage
from providers.ec2.tasks import ebs
from common.tasks import loopback
from common.tasks import volume
from common.tasks import locale
from common.tasks import apt
from common.tasks import bootstrap
from common.tasks import filesystem
from common.tasks import partitioning


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(tasklist, manifest):
	settings = manifest.plugins['prebootstrapped']
	skip_tasks = [ebs.Create,
	              loopback.Create,

	              filesystem.Format,
	              partitioning.PartitionVolume,
	              filesystem.TuneVolumeFS,
	              filesystem.AddXFSProgs,
	              filesystem.CreateBootMountDir,

	              apt.DisableDaemonAutostart,
	              locale.GenerateLocale,
	              bootstrap.MakeTarball,
	              bootstrap.Bootstrap]
	if manifest.volume['backing'] == 'ebs':
		if 'snapshot' in settings and settings['snapshot'] is not None:
			tasklist.add(CreateFromSnapshot)
			tasklist.remove(*skip_tasks)
		else:
			tasklist.add(Snapshot)
	else:
		if 'image' in settings and settings['image'] is not None:
			tasklist.add(CreateFromImage)
			tasklist.remove(*skip_tasks)
		else:
			tasklist.add(CopyImage)


def resolve_rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter)

	if manifest.volume['backing'] == 'ebs':
		counter_task(CreateFromSnapshot, volume.Delete)
	else:
		counter_task(CreateFromImage, volume.Delete)
