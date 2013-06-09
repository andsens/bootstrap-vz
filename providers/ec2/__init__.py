from manifest import Manifest


def tasklist(manifest):
	from common import TaskList
	import packages
	import ec2
	import host
	task_list = TaskList()
	task_list.extend([packages.HostPackages(),
	                  packages.ImagePackages(),
	                  ec2.GetCredentials(),
	                  host.GetInfo(),
	                  ec2.Connect(),
	                  host.InstallPackages()
                   ])

	return task_list
