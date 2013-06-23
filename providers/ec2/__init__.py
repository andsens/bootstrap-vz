from manifest import Manifest


def tasks(tasklist, manifest):
	from tasks import packages
	from tasks import ec2
	from tasks import host
	from tasks import ebs
	tasklist.add(packages.HostPackages(), packages.ImagePackages(), host.CheckPackages(),
	             ec2.GetCredentials(), host.GetInfo(), ec2.Connect())
	if manifest.volume['backing'] is 'ebs':
		tasklist.add(ebs.CreateVolume())
