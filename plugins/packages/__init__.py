

def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def resolve_tasks(tasklist, manifest):
	from tasks import AptSources, InstallRemotePackages, InstallLocalPackages
	packages = manifest.plugins['packages']
	if 'sources' in packages:
		tasklist.add(AptSources)
	if 'remote' in packages:
		tasklist.add(InstallRemotePackages)
	if 'local' in packages:
		tasklist.add(InstallLocalPackages)
