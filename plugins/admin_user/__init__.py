

def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def resolve_tasks(tasklist, manifest):
	import tasks
	from providers.ec2.tasks import initd
	if initd.AddEC2InitScripts in tasklist.tasks:
		tasklist.add(tasks.AdminUserCredentials)

	tasklist.add(tasks.AddSudoPackage,
	             tasks.CreateAdminUser,
	             tasks.PasswordlessSudo,
	             tasks.DisableRootLogin)
