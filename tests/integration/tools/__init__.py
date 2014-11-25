from bootstrapvz.common.tools import load_data

build_servers = load_data('build_servers.yml')

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


def bootstrap(manifest):
	# if 'build_host' in build_settings:
	# 	run = get_remote_run(build_settings)
	# else:
	# 	run = __import__('bootstrapvz.base.run')
	# run(manifest)
	from bootstrapvz.base.remote.remote import run
	run(manifest,
	    build_servers['virtualbox'],
	    debug=True,
	    dry_run=True)

	from ..image import Image
	return Image()

def test_instance(instance):
	pass
