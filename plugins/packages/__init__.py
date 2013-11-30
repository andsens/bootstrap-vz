

def validate_manifest(data, schema_validate):
	from os import path
	schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
	schema_validate(data, schema_path)


def tasks(tasklist, manifest):
	from tasks import AptSources, InstallRemotePackages, InstallLocalPackages
	if 'sources' in manifest.plugins['packages']:
		tasklist.add(AptSources)
	if 'remote' in manifest.plugins['packages']:
		tasklist.add(InstallRemotePackages)
	if 'local' in manifest.plugins['packages']:
		tasklist.add(InstallLocalPackages)
