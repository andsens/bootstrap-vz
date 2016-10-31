"""The Manifest module contains the manifest that providers and plugins use
to determine which tasks should be added to the tasklist, what arguments various
invocations should have etc..
"""
from bootstrapvz.common.exceptions import ManifestError
from bootstrapvz.common.tools import load_data, rel_path
import logging
log = logging.getLogger(__name__)


class Manifest(object):
    """This class holds all the information that providers and plugins need
    to perform the bootstrapping process. All actions that are taken originate from
    here. The manifest shall not be modified after it has been loaded.
    Currently, immutability is not enforced and it would require a fair amount of code
    to enforce it, instead we just rely on tasks behaving properly.
    """

    def __init__(self, path=None, data=None):
        """Initializer: Given a path we load, validate and parse the manifest.
        To create the manifest from dynamic data instead of the contents of a file,
        provide a properly constructed dict as the data argument.

        :param str path: The path to the manifest (ignored, when `data' is provided)
        :param str data: The manifest data, if it is not None, it will be used instead of the contents of `path'
        """
        if path is None and data is None:
            raise ManifestError('`path\' or `data\' must be provided')
        self.path = path

        self.metaschema = load_data(rel_path(__file__, 'metaschema.json'))

        self.load_data(data)
        self.load_modules()
        self.validate()
        self.parse()

    def load_data(self, data=None):
        """Loads the manifest and performs a basic validation.
        This function reads the manifest and performs some basic validation of
        the manifest itself to ensure that the properties required for initalization are accessible
        (otherwise the user would be presented with some cryptic error messages).
        """
        if data is None:
            self.data = load_data(self.path)
        else:
            self.data = data

        from . import validate_manifest
        # Validate the manifest with the base validation function in __init__
        validate_manifest(self.data, self.schema_validator, self.validation_error)

    def load_modules(self):
        """Loads the provider and the plugins.
        """
        # Get the provider name from the manifest and load the corresponding module
        provider_modname = 'bootstrapvz.providers.' + self.data['provider']['name']
        log.debug('Loading provider ' + self.data['provider']['name'])
        # Create a modules dict that contains the loaded provider and plugins
        import importlib
        self.modules = {'provider': importlib.import_module(provider_modname),
                        'plugins': [],
                        }
        # Run through all the plugins mentioned in the manifest and load them
        from pkg_resources import iter_entry_points
        if 'plugins' in self.data:
            for plugin_name in self.data['plugins'].keys():
                log.debug('Loading plugin ' + plugin_name)
                try:
                    # Internal bootstrap-vz plugins take precedence wrt. plugin name
                    modname = 'bootstrapvz.plugins.' + plugin_name
                    plugin = importlib.import_module(modname)
                except ImportError:
                    entry_points = list(iter_entry_points('bootstrapvz.plugins', name=plugin_name))
                    num_entry_points = len(entry_points)
                    if num_entry_points < 1:
                        raise
                    if num_entry_points > 1:
                        msg = ('Unable to load plugin {name}, '
                               'there are {num} entry points to choose from.'
                               .format(name=plugin_name, num=num_entry_points))
                        raise ImportError(msg)
                    plugin = entry_points[0].load()
                self.modules['plugins'].append(plugin)

    def validate(self):
        """Validates the manifest using the provider and plugin validation functions.
        Plugins are not required to have a validate_manifest function
        """

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
        self.name         = self.data['name']
        self.provider     = self.data['provider']
        self.bootstrapper = self.data['bootstrapper']
        self.volume       = self.data['volume']
        self.system       = self.data['system']
        from bootstrapvz.common.releases import get_release
        self.release      = get_release(self.system['release'])
        # The packages and plugins sections are not required
        self.packages     = self.data['packages'] if 'packages' in self.data else {}
        self.plugins      = self.data['plugins'] if 'plugins' in self.data else {}

    def schema_validator(self, data, schema_path):
        """This convenience function is passed around to all the validation functions
        so that they may run a json-schema validation by giving it the data and a path to the schema.

        :param dict data: Data to validate (normally the manifest data)
        :param str schema_path: Path to the json-schema to use for validation
        """
        import jsonschema

        schema = load_data(schema_path)

        try:
            jsonschema.validate(schema, self.metaschema)
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            self.validation_error(e.message, e.path)

    def validation_error(self, message, data_path=None):
        """This function is passed to all validation functions so that they may
        raise a validation error because a custom validation of the manifest failed.

        :param str message: Message to user about the error
        :param list data_path: A path to the location in the manifest where the error occurred
        :raises ManifestError: With absolute certainty
        """
        raise ManifestError(message, self.path, data_path)

    def __getstate__(self):
        return {'__class__': self.__module__ + '.' + self.__class__.__name__,
                'path': self.path,
                'metaschema': self.metaschema,
                'data': self.data}

    def __setstate__(self, state):
        self.path = state['path']
        self.metaschema = state['metaschema']
        self.load_data(state['data'])
        self.load_modules()
        self.validate()
        self.parse()
