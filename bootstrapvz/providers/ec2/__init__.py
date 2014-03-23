import tasks.packages
import tasks.connection
import tasks.host
import tasks.ami
import tasks.ebs
import tasks.filesystem
import tasks.boot
import tasks.network
import tasks.initd
from common.tasks import volume
from common.tasks import filesystem
from common.tasks import boot
from common.tasks import network
from common.tasks import initd
from common.tasks import partitioning
from common.tasks import loopback
from common.tasks import bootstrap
from common.tasks import security
from common.tasks import cleanup
from common.tasks import workspace


def initialize():
	# Regardless of of loglevel, we don't want boto debug stuff, it's very noisy
	import logging
	logging.getLogger('boto').setLevel(logging.INFO)


def validate_manifest(data, validator, error):
	import os.path
	validator(data, os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))

	from common.bytes import Bytes
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
	import common.task_sets
	taskset.update(common.task_sets.base_set)
	taskset.update(common.task_sets.mounting_set)
	taskset.update(common.task_sets.get_apt_set(manifest))
	taskset.update(common.task_sets.locale_set)
	taskset.update(common.task_sets.ssh_set)

	if manifest.volume['partitions']['type'] != 'none':
		taskset.update(common.task_sets.partitioning_set)

	taskset.update([tasks.host.AddExternalCommands,
	                tasks.packages.DefaultPackages,
	                tasks.connection.GetCredentials,
	                tasks.host.GetInfo,
	                tasks.ami.AMIName,
	                tasks.connection.Connect,

	                boot.BlackListModules,
	                boot.DisableGetTTYs,
	                security.EnableShadowConfig,
	                network.RemoveDNSInfo,
	                network.RemoveHostname,
	                network.ConfigureNetworkIF,
	                tasks.network.EnableDHCPCDDNS,
	                initd.AddExpandRoot,
	                initd.AddSSHKeyGeneration,
	                initd.RemoveHWClock,
	                tasks.initd.AddEC2InitScripts,
	                initd.InstallInitScripts,
	                initd.AdjustExpandRootScript,
	                cleanup.ClearMOTD,
	                cleanup.CleanTMP,

	                tasks.ami.RegisterAMI,
	                ])

	if manifest.system['bootloader'] == 'pvgrub':
		taskset.add(boot.AddGrubPackage)
		taskset.add(tasks.boot.ConfigurePVGrub)
	else:
		taskset.update(common.task_sets.bootloader_set.get(manifest.system['bootloader']))

	backing_specific_tasks = {'ebs': [tasks.ebs.Create,
	                                  tasks.ebs.Attach,
	                                  filesystem.FStab,
	                                  tasks.ebs.Snapshot],
	                          's3': [loopback.AddRequiredCommands,
	                                 loopback.Create,
	                                 volume.Attach,
	                                 tasks.filesystem.S3FStab,
	                                 tasks.ami.BundleImage,
	                                 tasks.ami.UploadImage,
	                                 tasks.ami.RemoveBundle]}
	taskset.update(backing_specific_tasks.get(manifest.volume['backing'].lower()))
	taskset.update([filesystem.Format,
	                volume.Detach,
	                volume.Delete,
	                ])

	if manifest.bootstrapper.get('tarball', False):
		taskset.add(bootstrap.MakeTarball)

	taskset.update(common.task_sets.get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		taskset.update(common.task_sets.boot_partition_set)


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
