import os.path
from bootstrapvz.common.tools import load_data

partial_manifests_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'manifests')
import glob
partial_yaml = glob.glob(os.path.join(partial_manifests_path, '*.yml'))
partial_json = glob.glob(os.path.join(partial_manifests_path, '*.json'))
manifests = {}
for path in partial_yaml + partial_json:
	manifests[os.path.basename(path)] = load_data(path)
build_settings = load_data(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'build_settings.yml'))
