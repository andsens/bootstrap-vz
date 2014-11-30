# Register deserialization handlers for objects
# that will pass between server and client
from bootstrapvz.remote import register_deserialization_handlers
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


def bootstrap(manifest, build_server):
	from bootstrapvz.remote.build_servers import LocalBuildServer
	if isinstance(build_server, LocalBuildServer):
		from bootstrapvz.base.main import run
		bootstrap_info = run(manifest)
	else:
		from bootstrapvz.remote.main import run
		bootstrap_info = run(manifest, build_server)
	return bootstrap_info


def test(instance):
	pass
