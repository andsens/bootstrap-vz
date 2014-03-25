"""The Manifest module contains the manifest that providers and plugins use
to determine which tasks should be added to the tasklist, what arguments various
invocations should have etc..
.. module:: manifest
"""
from common.tools import load_json
import logging
log = logging.getLogger(__name__)


class Manifest(object):
	"""This class holds all the information that providers and plugins need
	to perform the bootstrapping process. All actions that are taken originate from
	here. The manifest shall not be modified after it has been loaded.
	Currently, immutability is not enforced and it would require a fair amount of code
	to enforce it, instead we just rely on tasks behaving properly.
	"""
	def __init__(self, path):
		"""Initializer: Given a path we load, validate and parse the manifest.

		Args:
			path (str): The path to the manifest
		"""
		self.path = path
		self.load()
		self.validate()
		self.parse()

	def load(self):
		"""Loads the manifest.
		This function not only reads the manifest but also loads the specified provider and plugins.
		Once they are loaded, the initialize() function is called on each of them (if it exists).
		The provider must have an initialize function.
		"""
		# Load the manifest JSON using the loader in common.tools
		# It strips comments (which are invalid in strict json) before loading the data.
		self.data = load_json(self.path)
		# Get the provider name from the manifest and load the corresponding module
		provider_modname = 'providers.{provider}'.format(provider=self.data['provider'])
		log.debug('Loading provider `{modname}\''.format(modname=provider_modname))
		# Create a modules dict that contains the loaded provider and plugins
		self.modules = {'provider': __import__(provider_modname, fromlist=['providers']),
		                'plugins': [],
		                }
		# Run through all the plugins mentioned in the manifest and load them
		if 'plugins' in self.data:
			for plugin_name, plugin_data in self.data['plugins'].iteritems():
				modname = 'plugins.{plugin}'.format(plugin=plugin_name)
				log.debug('Loading plugin `{modname}\''.format(modname=modname))
				plugin = __import__(modname, fromlist=['plugins'])
				self.modules['plugins'].append(plugin)

		# Run the initialize function on the provider and plugins
		self.modules['provider'].initialize()
		for module in self.modules['plugins']:
			# Plugins are not required to have an initialize function
			init = getattr(module, 'initialize', None)
			if callable(init):
				init()

	def validate(self):
		"""Validates the manifest using the base, provider and plugin validation functions.
		Plugins are not required to have a validate_manifest function
		"""
		from . import validate_manifest
		# Validate the manifest with the base validation function in __init__
		validate_manifest(self.data, self.schema_validator, self.validation_error)
		# Run the provider validation
		self.modules['provider'].validate_manifest(self.data, self.schema_validator, self.validation_error)
		# Run the validation function for any plugin that has it
		for plugin in self.modules['plugins']:
			validate = getattr(plugin, 'validate_manifest', None)
			if callable(validate):
				validate(self.data, self.schema_validator, self.validation_error)

	def parse(self):
		"""Parses the manifest.
		Well... "parsing" is a big word.
		The function really just sets up some convenient attributes so that tasks
		don't have to access information with info.manifest.data['section']
		but can do it with info.manifest.section.
		"""
		self.provider     = self.data['provider']
		self.bootstrapper = self.data['bootstrapper']
		self.image        = self.data['image']
		self.volume       = self.data['volume']
		self.system       = self.data['system']
		# The packages and plugins section is not required
		self.packages     = self.data['packages'] if 'packages' in self.data else {}
		self.plugins      = self.data['plugins'] if 'plugins' in self.data else {}

	def load_json(self, path):
		"""Loads JSON. Unused and will be removed.
		Use common.tools.load_json instead
		"""
		import json
		from minify_json import json_minify
		with open(path) as stream:
			return json.loads(json_minify(stream.read(), False))

	def schema_validator(self, data, schema_path):
		"""This convenience function is passed around to all the validation functions
		so that they may run a json-schema validation by giving it the data and a path to the schema.

		Args:
			data (dict): Data to validate (normally the manifest data)
			schema_path (str): Path to the json-schema to use for validation
		"""
		import jsonschema
		schema = load_json(schema_path)
		try:
			jsonschema.validate(data, schema)
		except jsonschema.ValidationError as e:
			self.validation_error(e.message, e.path)

	def validation_error(self, message, json_path=None):
		"""This function is passed to all validation functions so that they may
		raise a validation error because a custom validation of the manifest failed.

		Args:
			message (str): Message to user about the error
			json_path (list): A path to the location in the manifest where the error occurred
		"""
		from common.exceptions import ManifestError
		raise ManifestError(message, self.path, json_path)
