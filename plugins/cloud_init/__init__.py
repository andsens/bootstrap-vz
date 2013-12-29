

def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def resolve_tasks(tasklist, manifest):
	import tasks
	import providers.ec2.tasks.initd as initd_ec2
	from common.tasks import initd

	if manifest.system['release'] in ['wheezy', 'stable']:
		tasklist.add(tasks.AddBackports)

	tasklist.add(tasks.AddCloudInitPackages,
	             tasks.SetMetadataSource)

	options = manifest.plugins['cloud_init']
	if 'username' in options:
		tasklist.add(tasks.SetUsername)
	if 'disable_modules' in options:
		tasklist.add(tasks.DisableModules)

	tasklist.remove(initd_ec2.AddEC2InitScripts,
	                initd.AddExpandRoot,
	                initd.AdjustExpandRootScript,
	                initd.AddSSHKeyGeneration)
