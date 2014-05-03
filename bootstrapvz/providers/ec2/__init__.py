import tasks.packages
import tasks.connection
import tasks.host
import tasks.ami
import tasks.ebs
import tasks.filesystem
import tasks.boot
import tasks.network
import tasks.initd
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import boot
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import workspace


def initialize():
	# Regardless of of loglevel, we don't want boto debug stuff, it's very noisy
	import logging
	logging.getLogger('boto').setLevel(logging.INFO)


def validate_manifest(data, validator, error):
	import os.path
	validator(data, os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))

	from bootstrapvz.common.bytes import Bytes
	if data['volume']['backing'] == 'ebs':
		volume_size = Bytes(0)
		for key, partition in data['volume']['partitions'].iteritems():
			if key != 'type':
				volume_size += Bytes(partition['size'])
		if volume_size % Bytes('1GiB') != 0:
			msg = ('The volume size must be a multiple of 1GiB when using EBS backing')
			error(msg, ['volume', 'partitions'])
	else:
		validator(data, os.path.join(os.path.dirname(__file__), 'manifest-schema-s3.json'))

	if data['virtualization'] == 'pvm' and data['system']['bootloader'] != 'pvgrub':
			error('Paravirtualized AMIs only support pvgrub as a bootloader', ['system', 'bootloader'])
	if data['virtualization'] == 'hvm' and data['system']['bootloader'] == 'pvgrub':
			error('HVM AMIs only support extlinux as a bootloader', ['system', 'bootloader'])
	if data['volume']['partitions']['type'] == 'none' and data['system']['bootloader'] == 'grub':
			error('Grub cannot boot from unpartitioned disks', ['system', 'bootloader'])


def resolve_tasks(taskset, manifest):
	from bootstrapvz.common import task_groups
	taskset.update(task_groups.get_standard_groups(manifest))
	taskset.update(task_groups.ssh_group)

	taskset.update([tasks.host.AddExternalCommands,
	                tasks.packages.DefaultPackages,
	                tasks.connection.GetCredentials,
	                tasks.ami.AMIName,
	                tasks.connection.Connect,

	                boot.BlackListModules,
	                boot.DisableGetTTYs,
	                tasks.network.EnableDHCPCDDNS,
	                initd.AddExpandRoot,
	                initd.RemoveHWClock,
	                tasks.initd.AddEC2InitScripts,
	                initd.InstallInitScripts,
	                initd.AdjustExpandRootScript,

	                tasks.ami.RegisterAMI,
	                ])

	if manifest.system['bootloader'] == 'pvgrub':
		taskset.add(boot.AddGrubPackage)
		taskset.add(tasks.boot.ConfigurePVGrub)

	if manifest.volume['backing'].lower() == 'ebs':
		taskset.update([tasks.host.GetInstanceMetadata,
		                tasks.ebs.Create,
		                tasks.ebs.Snapshot,
		                ])
		taskset.add(tasks.ebs.Attach)
		taskset.discard(volume.Attach)

	if manifest.volume['backing'].lower() == 's3':
		taskset.update([loopback.AddRequiredCommands,
		                tasks.host.SetRegion,
		                loopback.Create,
		                tasks.filesystem.S3FStab,
		                tasks.ami.BundleImage,
		                tasks.ami.UploadImage,
		                tasks.ami.RemoveBundle,
		                ])
		taskset.discard(filesystem.FStab)

	taskset.update([filesystem.Format,
	                volume.Delete,
	                ])


def resolve_rollback_tasks(taskset, manifest, counter_task):
	counter_task(tasks.ebs.Create, volume.Delete)
	counter_task(tasks.ebs.Attach, volume.Detach)

	counter_task(loopback.Create, volume.Delete)
	counter_task(volume.Attach, volume.Detach)

	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)

	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
	counter_task(tasks.ami.BundleImage, tasks.ami.RemoveBundle)
