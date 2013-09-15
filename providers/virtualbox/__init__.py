from manifest import Manifest
from tasks import packages
from common.tasks import packages as common_packages
from common.tasks import host
from common.tasks import volume as volume_tasks
from common.tasks import loopback
from common.tasks import partitioning
from common.tasks import filesystem
from common.tasks import bootstrap
from common.tasks import locale
from common.tasks import apt
from tasks import boot
from common.tasks import boot as common_boot
from common.tasks import security
from common.tasks import network
from common.tasks import initd
from common.tasks import cleanup
from common.tasks import workspace


def initialize():
	pass


def tasks(tasklist, manifest):
	tasklist.add(workspace.CreateWorkspace(),
	             packages.HostPackages(),
	             common_packages.HostPackages(),
	             packages.ImagePackages(),
	             common_packages.ImagePackages(),
	             host.CheckPackages(),

	             loopback.Create(),
	             volume_tasks.Attach(),
	             partitioning.PartitionVolume(),
	             partitioning.MapPartitions(),
	             filesystem.Format(),
	             filesystem.CreateMountDir(),
	             filesystem.MountRoot(),

	             bootstrap.Bootstrap(),
	             filesystem.MountSpecials(),
	             locale.GenerateLocale(),
	             locale.SetTimezone(),
	             apt.DisableDaemonAutostart(),
	             apt.AptSources(),
	             apt.AptUpgrade(),
	             boot.ConfigureGrub(),
	             filesystem.FStab(),
	             common_boot.BlackListModules(),
	             common_boot.DisableGetTTYs(),
	             security.EnableShadowConfig(),
	             security.DisableSSHPasswordAuthentication(),
	             security.DisableSSHDNSLookup(),
	             network.RemoveDNSInfo(),
	             network.ConfigureNetworkIF(),
	             network.ConfigureDHCP(),
	             initd.ResolveInitScripts(),
	             initd.InstallInitScripts(),
	             cleanup.ClearMOTD(),
	             cleanup.ShredHostkeys(),
	             cleanup.CleanTMP(),
	             apt.PurgeUnusedPackages(),
	             apt.AptClean(),
	             apt.EnableDaemonAutostart(),
	             filesystem.UnmountSpecials(),

	             filesystem.UnmountRoot(),
	             partitioning.UnmapPartitions(),
	             volume_tasks.Detach(),
	             filesystem.DeleteMountDir(),
	             loopback.MoveImage(),
	             workspace.DeleteWorkspace())

	if manifest.bootstrapper.get('tarball', False):
		tasklist.add(bootstrap.MakeTarball())

	partitions = manifest.volume['partitions']
	import re
	for key in ['boot', 'root']:
		if key not in partitions:
			continue
		if re.match('^ext[2-4]$', partitions[key]['filesystem']) is not None:
			tasklist.add(filesystem.TuneVolumeFS())
			break
	for key in ['boot', 'root']:
		if key not in partitions:
			continue
		if partitions[key]['filesystem'] == 'xfs':
			tasklist.add(filesystem.AddXFSProgs())
			break

	if 'boot' in manifest.volume['partitions']:
		tasklist.add(filesystem.MountBoot(), filesystem.UnmountBoot())


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter())

	counter_task(loopback.Create, volume_tasks.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(filesystem.MountSpecials, filesystem.UnmountSpecials)
	counter_task(filesystem.MountBoot, filesystem.UnmountBoot)
	counter_task(volume_tasks.Attach, volume_tasks.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
