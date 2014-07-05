

def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	import tasks
	from bootstrapvz.providers.ec2.tasks import initd
	if initd.AddEC2InitScripts in taskset:
		taskset.add(tasks.AdminUserCredentials)

	taskset.update([tasks.AddSudoPackage,
	                tasks.CreateAdminUser,
	                tasks.PasswordlessSudo,
	                tasks.DisableRootLogin,
	                ])
