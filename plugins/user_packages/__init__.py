

def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def tasks(tasklist, manifest):
	from user_packages import AddUserPackages, AddLocalUserPackages
	if 'repo' in manifest.plugins['user_packages']:
		tasklist.add(AddUserPackages)
	if 'local' in manifest.plugins['user_packages']:
		tasklist.add(AddLocalUserPackages)
