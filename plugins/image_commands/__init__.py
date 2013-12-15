

def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def resolve_tasks(tasklist, manifest):
	from tasks import ImageExecuteCommand
	tasklist.add(ImageExecuteCommand)
