from manifest import Manifest
from tasks import packages
from tasks import connection
from tasks import host
from tasks import ebs


def tasks(tasklist, manifest):
	tasklist.add(packages.HostPackages(), packages.ImagePackages(), host.CheckPackages(),
	             connection.GetCredentials(), host.GetInfo(), connection.Connect())
	if manifest.volume['backing'].lower() == 'ebs':
		tasklist.add(ebs.CreateVolume(), ebs.AttachVolume())

	from common.tasks import TriggerRollback
	tasklist.add(TriggerRollback())


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]
	if manifest.volume['backing'].lower() == 'ebs':
		if ebs.CreateVolume in completed and ebs.DeleteVolume not in completed:
			tasklist.add(ebs.DeleteVolume())
		if ebs.AttachVolume in completed and ebs.DetachVolume not in completed:
			tasklist.add(ebs.DetachVolume())
