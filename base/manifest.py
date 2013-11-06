import logging
log = logging.getLogger(__name__)


def load_manifest(path):
	data = load_json(path)

	provider_name = data['provider']
	provider = __import__('providers.{module}'.format(module=provider_name), fromlist=['providers'])
	init = getattr(provider, 'initialize', None)
	if callable(init):
		init()
	log.debug('Loaded provider `%s\'', provider_name)
	manifest = provider.Manifest(path)

	manifest.validate(data)
	manifest.load_plugins(data)
	manifest.parse(data)
	return (provider, manifest)


def load_json(path):
	import json
	from minify_json import json_minify
	with open(path) as stream:
		return json.loads(json_minify(stream.read(), False))


class Manifest(object):
	def __init__(self, path):
		self.path = path

	def validate(self, data):
		from os import path
		schema_path = path.join(path.dirname(__file__), 'manifest-schema.json')
		self.schema_validate(data, schema_path)

	def schema_validate(self, data, schema_path):
		import jsonschema
		schema = load_json(schema_path)
		try:
			jsonschema.validate(data, schema)
		except jsonschema.ValidationError as e:
			from common.exceptions import ManifestError
			raise ManifestError(e.message, self, e.path)

	def parse(self, data):
		self.provider = data['provider']
		self.bootstrapper = data['bootstrapper']
		if 'mirror' not in self.bootstrapper:
			self.bootstrapper['mirror'] = 'http://http.debian.net/debian'
		self.volume = data['volume']
		self.system = data['system']
		self.plugins = data['plugins'] if 'plugins' in data else {}

	def load_plugins(self, data):
		self.loaded_plugins = []
		if 'plugins' in data:
			for plugin_name, plugin_data in data['plugins'].iteritems():
				if plugin_data['enabled']:
					modname = 'plugins.{plugin_name}'.format(plugin_name=plugin_name)
					plugin = __import__(modname, fromlist=['plugins'])
					init = getattr(plugin, 'initialize', None)
					if callable(init):
						init()
					log.debug('Loaded plugin `%s\'', plugin_name)
					self.loaded_plugins.append(plugin)
					validate = getattr(plugin, 'validate_manifest', None)
					if callable(validate):
						validate(data, self.schema_validate)
