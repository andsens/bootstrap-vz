import os.path
import glob
from bootstrapvz.common.tools import load_data

partial_json = glob.glob(os.path.join(os.path.dirname(__file__), '*.yml'))
partial_yaml = glob.glob(os.path.join(os.path.dirname(__file__), '*.json'))

partials = {}
for path in partial_json + partial_yaml:
	key = os.path.splitext(os.path.basename(path))[0]
	if key in partials:
		msg = 'Error when loading partial manifests: The partial {key} exists twice'.format(key=key)
		raise Exception(msg)
	partials[key] = load_data(path)

import random
import string
pool = string.ascii_uppercase + string.ascii_lowercase + string.digits
random_password = ''.join(random.choice(pool) for _ in range(16))
partials['root_password']['plugins']['root_password']['password'] = random_password


def merge_manifest_data(standard_partials=[], custom=[]):
	import yaml
	manifest_data = [partials[name] for name in standard_partials]
	manifest_data.extend(yaml.load(data) for data in custom)
	return merge_dicts(*manifest_data)


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
