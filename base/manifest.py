import logging
log = logging.getLogger(__name__)


def load_manifest(path):
	data = load_json(path)

	provider = __import__('providers.{module}'.format(module=data['provider']), fromlist=['providers'])
	manifest = provider.Manifest(path)

	manifest.validate(data)
	manifest.parse(data)
	manifest.load_plugins()
	return (provider, manifest)

def load_json(path):
	import json
	from minify_json import json_minify
	with open(path) as stream:
		return json.loads(json_minify(stream.read(), False))

class Manifest(object):
	def __init__(self, path):
		self.path = path

	def validate(self, data, schema_path=None):
		if schema_path is not None:
			from json_schema_validator.validator import Validator
			from json_schema_validator.schema import Schema
			from json_schema_validator.errors import ValidationError
			schema = Schema(load_json(schema_path))
			try:
				Validator.validate(schema, data)
			except ValidationError as e:
				from common.exceptions import ManifestError
				raise ManifestError(e.message, self)

	def parse(self, data):
		self.provider = data['provider']
		self.volume   = data['volume']
		self.system   = data['system']
		self.plugins  = data['plugins']

	def load_plugins(self):
		self.loaded_plugins = []
		for modname in self.plugins.keys():
			if self.plugins[modname]['enabled']:
				plugin_name = 'plugins.{module}'.format(module=modname)
				plugin = __import__(plugin_name, fromlist=['plugins'])
				log.debug('Loaded plugin %s', plugin_name)
				self.loaded_plugins.append(plugin)
