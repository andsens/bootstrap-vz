from manifest import Manifest


def tasklist(manifest):
	from common import TaskList
	from tasks import packages
	from tasks import ec2
	from tasks import host
	task_list = TaskList()
	task_list.extend([packages.HostPackages(),
	                  packages.ImagePackages(),
	                  ec2.GetCredentials(),
	                  host.GetInfo(),
	                  ec2.Connect(),
	                  host.InstallPackages()
                   ])

	return task_list
