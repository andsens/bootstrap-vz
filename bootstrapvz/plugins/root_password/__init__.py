

def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(taskset, manifest):
	from bootstrapvz.common.tasks.security import DisableSSHPasswordAuthentication
	from tasks import SetRootPassword
	taskset.discard(DisableSSHPasswordAuthentication)
	taskset.add(SetRootPassword)
