from manifest import Manifest


def modify_tasklist(tasklist, manifest):
	from tasks import packages
	from tasks import ec2
	from tasks import host
	from tasks import ebs
	tasklist.extend([packages.HostPackages(),
	                 packages.ImagePackages(),
	                 host.CheckPackages(),
	                 ec2.GetCredentials(),
	                 host.GetInfo(),
	                 ec2.Connect(),
	                 ebs.CreateVolume(),
                  ])
