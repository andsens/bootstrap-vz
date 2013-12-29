from manifest import Manifest
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


def resolve_tasks(tasklist, manifest):
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

	tasklist.add(tasks.host.HostDependencies,
	             tasks.packages.DefaultPackages,
	             tasks.connection.GetCredentials,
	             tasks.host.GetInfo,
	             tasks.ami.AMIName,
	             tasks.connection.Connect,

	             boot.BlackListModules,
	             boot.DisableGetTTYs,
	             security.EnableShadowConfig,
	             network.RemoveDNSInfo,
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

	             tasks.ami.RegisterAMI)

	if manifest.virtualization == 'pvm':
		tasklist.add(tasks.boot.ConfigurePVGrub)
	else:
		tasklist.add(boot.InstallGrub)

	backing_specific_tasks = {'ebs': [tasks.ebs.Create,
	                                  tasks.ebs.Attach,
	                                  filesystem.FStab,
	                                  tasks.ebs.Snapshot],
	                          's3': [loopback.Create,
	                                 volume.Attach,
	                                 tasks.filesystem.S3FStab,
	                                 tasks.ami.BundleImage,
	                                 tasks.ami.UploadImage,
	                                 tasks.ami.RemoveBundle]}
	tasklist.add(*backing_specific_tasks.get(manifest.volume['backing'].lower()))
	tasklist.add(filesystem.Format,
	             volume.Detach,
	             volume.Delete)

	if manifest.bootstrapper.get('tarball', False):
		tasklist.add(bootstrap.MakeTarball)

	from common.task_sets import get_fs_specific_set
	tasklist.add(*get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		from common.task_sets import boot_partition_set
		tasklist.add(*boot_partition_set)


def resolve_rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter)

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
