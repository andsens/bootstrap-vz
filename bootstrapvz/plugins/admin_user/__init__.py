

def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	import tasks
	from bootstrapvz.common.tasks import ssh
	from bootstrapvz.providers.ec2.tasks import initd
	if initd.AddEC2InitScripts in taskset:
		taskset.add(tasks.AdminUserCredentials)

	from bootstrapvz.common.releases import jessie
	if manifest.release < jessie:
		taskset.update([ssh.DisableRootLogin])

	taskset.update([tasks.AddSudoPackage,
	                tasks.CreateAdminUser,
	                tasks.PasswordlessSudo,
	                ])
