from manifest import Manifest
from tasks import packages
from common.tasks import packages as common_packages
from common.tasks import host
from common.tasks import loopback
from common.tasks import parted
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
from common.tasks import loopback


def initialize():
	pass


def tasks(tasklist, manifest):
	tasklist.add(packages.HostPackages(),
	             common_packages.HostPackages(),
	             packages.ImagePackages(),
	             common_packages.ImagePackages(),
	             host.CheckPackages(),

	             loopback.CreateQemuImg(),
	             loopback.Attach(),
	             parted.PartitionVolume(),
	             parted.MapPartitions(),
	             parted.FormatPartitions(),
	             filesystem.CreateMountDir(),
	             filesystem.MountVolume(),

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

	             filesystem.UnmountVolume(),
	             parted.UnmapPartitions(),
	             loopback.Detach(),
	             filesystem.DeleteMountDir())

	if manifest.bootstrapper['tarball']:
		tasklist.add(bootstrap.MakeTarball())

	filesystem_specific_tasks = {'xfs': [filesystem.AddXFSProgs()],
	                             'ext2': [filesystem.TuneVolumeFS()],
	                             'ext3': [filesystem.TuneVolumeFS()],
	                             'ext4': [filesystem.TuneVolumeFS()]}
	tasklist.add(*filesystem_specific_tasks.get(manifest.volume['filesystem'].lower()))


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter())

	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(parted.MapPartitions, parted.UnmapPartitions)
	counter_task(filesystem.MountVolume, filesystem.UnmountVolume)
	counter_task(filesystem.MountSpecials, filesystem.UnmountSpecials)
	counter_task(loopback.Attach, loopback.Detach)
