from manifest import Manifest


def modify_tasklist(tasklist, manifest):
	from tasks import packages
	from tasks import ec2
	from tasks import host
	tasklist.extend([packages.HostPackages(),
	                 packages.ImagePackages(),
	                 ec2.GetCredentials(),
	                 host.GetInfo(),
	                 ec2.Connect(),
	                 host.InstallPackages()
                  ])
