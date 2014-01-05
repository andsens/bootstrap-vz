import logging
log = logging.getLogger(__name__)


class Manifest(object):
	def __init__(self, path):
		self.path = path
		self.load()
		self.validate()
		self.parse()

	def load(self):
		self.data = self.load_json(self.path)
		provider_modname = 'providers.{provider}'.format(provider=self.data['provider'])
		log.debug('Loading provider `{modname}\''.format(modname=provider_modname))
		self.modules = {'provider': __import__(provider_modname, fromlist=['providers']),
		                'plugins': [],
		                }
		if 'plugins' in self.data:
			for plugin_name, plugin_data in self.data['plugins'].iteritems():
				modname = 'plugins.{plugin}'.format(plugin=plugin_name)
				log.debug('Loading plugin `{modname}\''.format(modname=modname))
				plugin = __import__(modname, fromlist=['plugins'])
				self.modules['plugins'].append(plugin)

		self.modules['provider'].initialize()
		for module in self.modules['plugins']:
			init = getattr(module, 'initialize', None)
			if callable(init):
				init()

	def validate(self):
		from . import validate_manifest
		validate_manifest(self.data, self.schema_validator, self.validation_error)
		self.modules['provider'].validate_manifest(self.data, self.schema_validator, self.validation_error)
		for plugin in self.modules['plugins']:
			validate = getattr(plugin, 'validate_manifest', None)
			if callable(validate):
				validate(self.data, self.schema_validator, self.validation_error)

	def parse(self):
		self.provider     = self.data['provider']
		self.bootstrapper = self.data['bootstrapper']
		self.image        = self.data['image']
		self.volume       = self.data['volume']
		self.system       = self.data['system']
		self.packages     = self.data['packages']
		self.plugins      = self.data['plugins'] if 'plugins' in self.data else {}

	def load_json(self, path):
		import json
		from minify_json import json_minify
		with open(path) as stream:
			return json.loads(json_minify(stream.read(), False))

	def schema_validator(self, data, schema_path):
		import jsonschema
		schema = self.load_json(schema_path)
		try:
			jsonschema.validate(data, schema)
		except jsonschema.ValidationError as e:
			self.validation_error(e.message, e.path)

	def validation_error(self, message, json_path=None):
		from common.exceptions import ManifestError
		raise ManifestError(message, self.path, json_path)
