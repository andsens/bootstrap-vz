from manifest import Manifest
import logging
from tasks import packages
from tasks import connection
from tasks import host
from tasks import ami
from tasks import ebs
from tasks import loopback
from tasks import filesystem
from common.tasks import bootstrap
from tasks import locale
from common.tasks import apt
from tasks import boot
from common.tasks import boot as common_boot
from tasks import security
from tasks import network
from tasks import initd
from tasks import cleanup


def initialize():
	# Regardless of of loglevel, we don't want boto debug stuff, it's very noisy
	logging.getLogger('boto').setLevel(logging.INFO)


def tasks(tasklist, manifest):
	tasklist.add(packages.HostPackages(),
	             packages.ImagePackages(),
	             host.CheckPackages(),
	             connection.GetCredentials(),
	             host.GetInfo(),
	             ami.AMIName(),
	             connection.Connect(),

	             filesystem.FormatVolume(),
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
	             filesystem.ModifyFstab(),
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
	             filesystem.DeleteMountDir(),
	             ami.RegisterAMI())

	if manifest.bootstrapper['tarball']:
		tasklist.add(bootstrap.MakeTarball())

	backing_specific_tasks = {'ebs': [ebs.Create(),
	                                  ebs.Attach(),
	                                  ebs.Detach(),
	                                  ebs.Snapshot(),
	                                  ebs.Delete()],
	                          's3': [loopback.Create(),
	                                 loopback.Attach(),
	                                 loopback.Detach(),
	                                 ami.BundleImage(),
	                                 ami.UploadImage(),
	                                 loopback.Delete(),
	                                 ami.RemoveBundle()]}
	tasklist.add(*backing_specific_tasks.get(manifest.volume['backing'].lower()))

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

	if manifest.volume['backing'].lower() == 'ebs':
		counter_task(ebs.Create, ebs.Delete)
		counter_task(ebs.Attach, ebs.Detach)
	if manifest.volume['backing'].lower() == 's3':
		counter_task(loopback.Create, loopback.Delete)
		counter_task(loopback.Attach, loopback.Detach)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(filesystem.MountVolume, filesystem.UnmountVolume)
	counter_task(filesystem.MountSpecials, filesystem.UnmountSpecials)
