import os.path
import glob
from bootstrapvz.common.tools import load_data

partial_json = glob.glob(os.path.join(os.path.dirname(__file__), '*.yml'))
partial_yaml = glob.glob(os.path.join(os.path.dirname(__file__), '*.json'))

def dictkey(path):
	return 
# yaml overrides json
partials = {}
for path in partial_json + partial_yaml:
	key = os.path.splitext(os.path.basename(path))[0]
	partials[key] = load_data(path)
	
