from manifest import Manifest
import logging
from tasks import packages
from tasks import connection
from tasks import host
from tasks import ebs
from tasks import filesystem
from tasks import bootstrap
from tasks import config


def initialize():
	# Regardless of of loglevel, we don't want boto debug stuff, it's very noisy
	logging.getLogger('boto').setLevel(logging.INFO)


def tasks(tasklist, manifest):
	tasklist.add(packages.HostPackages(),
	             packages.ImagePackages(),
	             host.CheckPackages(),
	             connection.GetCredentials(),
	             host.GetInfo(),
	             connection.Connect())
	if manifest.volume['backing'].lower() == 'ebs':
		tasklist.add(ebs.CreateVolume(),
		             ebs.AttachVolume())
	tasklist.add(filesystem.FormatVolume())
	if manifest.volume['filesystem'].lower() == 'xfs':
		tasklist.add(filesystem.AddXFSProgs())
	import re
	if re.search('ext.', manifest.volume['filesystem'].lower()):
		tasklist.add(filesystem.TuneVolumeFS())
	tasklist.add(filesystem.CreateMountDir(), filesystem.MountVolume())
	if manifest.bootstrapper['tarball']:
		tasklist.add(bootstrap.MakeTarball())
	tasklist.add(bootstrap.Bootstrap(),
	             filesystem.MountSpecials(),
	             config.GenerateLocale(),
	             config.SetTimezone(),
	             config.AptSources())

	from common.tasks import TriggerRollback
	tasklist.add(TriggerRollback())


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter())

	if manifest.volume['backing'].lower() == 'ebs':
		counter_task(ebs.CreateVolume, ebs.DeleteVolume)
		counter_task(ebs.AttachVolume, ebs.DetachVolume)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(filesystem.MountVolume, filesystem.UnmountVolume)
	counter_task(filesystem.MountSpecials, filesystem.UnmountSpecials)
