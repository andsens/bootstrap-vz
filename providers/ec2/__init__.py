from manifest import Manifest
import logging
from tasks import packages
from tasks import connection
from tasks import host
from tasks import ami
from common.tasks import volume as volume_tasks
from tasks import ebs
from common.tasks import partitioning
from common.tasks import loopback
from common.tasks import filesystem as common_filesystem
from tasks import filesystem
from common.tasks import bootstrap
from tasks import boot
from common.tasks import boot as common_boot
from common.tasks import security
from tasks import network
from common.tasks import network as common_network
from tasks import initd
from common.tasks import initd as common_initd
from common.tasks import cleanup
from common.tasks import workspace


def initialize():
	# Regardless of of loglevel, we don't want boto debug stuff, it's very noisy
	logging.getLogger('boto').setLevel(logging.INFO)


def tasks(tasklist, manifest):
	from common.task_sets import base_set
	from common.task_sets import mounting_set
	from common.task_sets import apt_set
	from common.task_sets import locale_set
	from common.task_sets import ssh_set
	tasklist.add(*base_set)
	tasklist.add(*mounting_set)
	tasklist.add(*apt_set)
	tasklist.add(*locale_set)
	tasklist.add(*ssh_set)

	if manifest.volume['partitions']['type'] != 'none':
		from common.task_sets import partitioning_set
		tasklist.add(*partitioning_set)

	tasklist.add(packages.HostPackages,
	             packages.ImagePackages,
	             connection.GetCredentials,
	             host.GetInfo,
	             ami.AMIName,
	             connection.Connect,

	             boot.ConfigureGrub,
	             common_boot.BlackListModules,
	             common_boot.DisableGetTTYs,
	             security.EnableShadowConfig,
	             common_network.RemoveDNSInfo,
	             common_network.ConfigureNetworkIF,
	             network.EnableDHCPCDDNS,
	             common_initd.ResolveInitScripts,
	             initd.AddEC2InitScripts,
	             common_initd.InstallInitScripts,
	             initd.AdjustExpandVolumeScript,
	             cleanup.ClearMOTD,
	             cleanup.CleanTMP,

	             ami.RegisterAMI)

	backing_specific_tasks = {'ebs': [ebs.Create,
	                                  ebs.Attach,
	                                  common_filesystem.FStab,
	                                  ebs.Snapshot],
	                          's3': [loopback.Create,
	                                 volume_tasks.Attach,
	                                 filesystem.S3FStab,
	                                 ami.BundleImage,
	                                 ami.UploadImage,
	                                 ami.RemoveBundle]}
	tasklist.add(*backing_specific_tasks.get(manifest.volume['backing'].lower()))
	tasklist.add(common_filesystem.Format,
	             volume_tasks.Detach,
	             volume_tasks.Delete)

	if manifest.bootstrapper.get('tarball', False):
		tasklist.add(bootstrap.MakeTarball)

	from common.task_sets import get_fs_specific_set
	tasklist.add(*get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		from common.task_sets import boot_partition_set
		tasklist.add(*boot_partition_set)


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter)

	counter_task(ebs.Create, volume_tasks.Delete)
	counter_task(ebs.Attach, volume_tasks.Detach)

	counter_task(loopback.Create, volume_tasks.Delete)
	counter_task(volume_tasks.Attach, volume_tasks.Detach)

	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(common_filesystem.CreateMountDir, common_filesystem.DeleteMountDir)
	counter_task(common_filesystem.MountSpecials, common_filesystem.UnmountSpecials)

	counter_task(common_filesystem.MountRoot, common_filesystem.UnmountRoot)
	counter_task(common_filesystem.MountBoot, common_filesystem.UnmountBoot)
	counter_task(volume_tasks.Attach, volume_tasks.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
	counter_task(ami.BundleImage, ami.RemoveBundle)
