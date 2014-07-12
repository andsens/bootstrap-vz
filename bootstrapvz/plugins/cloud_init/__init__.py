

def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	import tasks
	import bootstrapvz.providers.ec2.tasks.initd as initd_ec2
	from bootstrapvz.common.tasks import apt
	from bootstrapvz.common.tasks import initd
	from bootstrapvz.common.tasks import ssh

	from bootstrapvz.common.tools import get_codename
	if get_codename(manifest.system['release']) == 'wheezy':
		taskset.add(apt.AddBackports)

	taskset.update([tasks.SetMetadataSource,
	                tasks.AddCloudInitPackages,
	                ])

	options = manifest.plugins['cloud_init']
	if 'username' in options:
		taskset.add(tasks.SetUsername)
	if 'disable_modules' in options:
		taskset.add(tasks.DisableModules)

	taskset.discard(initd_ec2.AddEC2InitScripts)
	taskset.discard(initd.AddExpandRoot)
	taskset.discard(initd.AdjustExpandRootScript)
	taskset.discard(ssh.AddSSHKeyGeneration)
