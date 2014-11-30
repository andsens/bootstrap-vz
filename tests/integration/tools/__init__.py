from bootstrapvz.common.tools import load_data
from build_servers import LocalBuildServer
from build_servers import RemoteBuildServer

# Register deserialization handlers for objects
# that will pass between server and client
from bootstrapvz.base.remote import register_deserialization_handlers
register_deserialization_handlers()


# Snatched from here: http://stackoverflow.com/a/7205107
def merge_dicts(*args):
	def merge(a, b, path=None):
		if path is None:
			path = []
		for key in b:
			if key in a:
				if isinstance(a[key], dict) and isinstance(b[key], dict):
					merge(a[key], b[key], path + [str(key)])
				elif a[key] == b[key]:
					pass
				else:
					raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
			else:
						a[key] = b[key]
		return a
	return reduce(merge, args, {})


def pick_build_server(manifest):
	if manifest['provider']['name'] == 'ec2':
		img_type = 'ec2-' + manifest['volume']['backing']
	else:
		img_type = manifest['provider']['name']

	# tox makes sure that the cwd is the project root
	build_servers = load_data('build_servers.yml')
	settings = next((server for name, server in build_servers.iteritems() if img_type in server['can_bootstrap']), None)
	if settings['type'] == 'local':
		return LocalBuildServer(settings)
	else:
		return RemoteBuildServer(settings)


def bootstrap(manifest, build_server):
	if isinstance(build_server, LocalBuildServer):
		from bootstrapvz.base.main import run
		bootstrap_info = run(manifest)
	else:
		from bootstrapvz.base.remote.remote import run
		bootstrap_info = run(manifest, build_server.settings)
	return bootstrap_info


def test(instance):
	pass
