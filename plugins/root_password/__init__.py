

def tasks(tasklist, manifest):
	from common.tasks.security import DisableSSHPasswordAuthentication
	from tasks import SetRootPassword
	tasklist.replace(DisableSSHPasswordAuthentication, SetRootPassword())


def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)
