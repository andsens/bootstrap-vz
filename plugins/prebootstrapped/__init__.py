

def tasks(tasklist, manifest):
	from ebs import CreateVolumeFromSnapshot
	from providers.ec2.tasks.ebs import CreateVolume
	tasklist.replace(CreateVolume, CreateVolumeFromSnapshot())
