from tasks import Snapshot
from tasks import CopyImage
from tasks import CreateFromSnapshot
from tasks import CreateFromImage
from bootstrapvz.providers.ec2.tasks import ebs
from bootstrapvz.providers.virtualbox.tasks import guest_additions
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import locale
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import bootstrap
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import partitioning


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
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
	              bootstrap.Bootstrap,
	              guest_additions.InstallGuestAdditions,
	              ]
	if manifest.volume['backing'] == 'ebs':
		if 'snapshot' in settings and settings['snapshot'] is not None:
			taskset.add(CreateFromSnapshot)
			[taskset.discard(task) for task in skip_tasks]
		else:
			taskset.add(Snapshot)
	else:
		if 'image' in settings and settings['image'] is not None:
			taskset.add(CreateFromImage)
			[taskset.discard(task) for task in skip_tasks]
		else:
			taskset.add(CopyImage)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	if manifest.volume['backing'] == 'ebs':
		counter_task(taskset, CreateFromSnapshot, volume.Delete)
	else:
		counter_task(taskset, CreateFromImage, volume.Delete)
