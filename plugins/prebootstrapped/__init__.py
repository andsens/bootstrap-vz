

def tasks(tasklist, manifest):
	from tasks import CreateVolumeFromSnapshot
	from providers.ec2.tasks import ebs
	from providers.ec2.tasks import bootstrap
	from providers.ec2.tasks import filesystem
	tasklist.replace(ebs.CreateVolume, CreateVolumeFromSnapshot())
	tasklist.remove(filesystem.FormatVolume,
	                filesystem.TuneVolumeFS,
	                filesystem.AddXFSProgs,
	                bootstrap.MakeTarball,
	                bootstrap.Bootstrap)
