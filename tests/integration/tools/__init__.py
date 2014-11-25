

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


def bootstrap(manifest, build_settings):
	# if 'build_host' in build_settings:
	# 	run = get_remote_run(build_settings)
	# else:
	# 	run = __import__('bootstrapvz.base.run')
	# run(manifest)
	from ..image import Image
	return Image()
