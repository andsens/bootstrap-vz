from manifest import Manifest
from tasks import packages
from common.tasks import packages as common_packages
from tasks import host
from tasks import filesystem
from common.tasks import filesystem as common_filesystem
from common.tasks import bootstrap
from common.tasks import locale
from common.tasks import apt
from tasks import boot
from common.tasks import boot as common_boot
from tasks import context
from common.tasks import security
from common.tasks import network
from common.tasks import initd
from common.tasks import cleanup


def initialize():
	pass


def tasks(tasklist, manifest):
	tasklist.add(packages.HostPackages(),
	             common_packages.HostPackages(),
	             packages.ImagePackages(),
	             common_packages.ImagePackages(),
	             host.CheckPackages(),

	             filesystem.FormatVolume(),
	             common_filesystem.CreateMountDir(),
	             filesystem.MountVolume(),

	             bootstrap.Bootstrap(),
	             common_filesystem.MountSpecials(),
	             locale.GenerateLocale(),
	             context.OpenNebulaContext(),
	             locale.SetTimezone(),
	             apt.DisableDaemonAutostart(),
	             apt.AptSources(),
	             #No network for the moment, skip
	             #apt.AptUpgrade(),
	             boot.ConfigureGrub(),
	             filesystem.ModifyFstab(),
	             common_boot.BlackListModules(),
	             common_boot.DisableGetTTYs(),
	             security.EnableShadowConfig(),
	             security.SetRootPassword(),
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
	             common_filesystem.UnmountSpecials(),

	             filesystem.UnmountVolume(),
	             common_filesystem.DeleteMountDir())

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

	counter_task(common_filesystem.CreateMountDir, common_filesystem.DeleteMountDir)
	counter_task(filesystem.MountVolume, filesystem.UnmountVolume)
	counter_task(common_filesystem.MountSpecials, common_filesystem.UnmountSpecials)
