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
	
