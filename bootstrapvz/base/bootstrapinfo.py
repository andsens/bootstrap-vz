

class BootstrapInformation(object):
	"""The BootstrapInformation class holds all information about the bootstrapping process.
	The nature of the attributes of this class are rather diverse.
	Tasks may set their own attributes on this class for later retrieval by another task.
	Information that becomes invalid (e.g. a path to a file that has been deleted) must be removed.
	"""
	def __init__(self, manifest=None, debug=False):
		"""Instantiates a new bootstrap info object.

		:param Manifest manifest: The manifest
		:param bool debug: Whether debugging is turned on
		"""
		# Set the manifest attribute.
		self.manifest = manifest
		self.debug = debug

		# Create a run_id. This id may be used to uniquely identify the currrent bootstrapping process
		import random
		self.run_id = '{id:08x}'.format(id=random.randrange(16 ** 8))

		# Define the path to our workspace
		import os.path
		self.workspace = os.path.join(manifest.bootstrapper['workspace'], self.run_id)

		# Load all the volume information
		from fs import load_volume
		self.volume = load_volume(self.manifest.volume, manifest.system['bootloader'])

		# The default apt mirror
		self.apt_mirror = self.manifest.packages.get('mirror', 'http://http.debian.net/debian')

		from bootstrapvz.common.tools import get_codename
		self.release_codename = get_codename(self.manifest.system['release'])

		# Create the manifest_vars dictionary
		self.manifest_vars = self.__create_manifest_vars(self.manifest, {'apt_mirror': self.apt_mirror})

		# Keep a list of apt sources,
		# so that tasks may add to that list without having to fiddle with apt source list files.
		from pkg.sourceslist import SourceLists
		self.source_lists = SourceLists(self.manifest_vars)
		# Keep a list of apt preferences
		from pkg.preferenceslist import PreferenceLists
		self.preference_lists = PreferenceLists(self.manifest_vars)
		# Keep a list of packages that should be installed, tasks can add and remove things from this list
		from pkg.packagelist import PackageList
		self.packages = PackageList(self.manifest_vars, self.source_lists)

		# These sets should rarely be used and specify which packages the debootstrap invocation
		# should be called with.
		self.include_packages = set()
		self.exclude_packages = set()

		# Dictionary to specify which commands are required on the host.
		# The keys are commands, while the values are either package names or urls
		# that hint at how a command may be made available.
		self.host_dependencies = {}

		# Lists of startup scripts that should be installed and disabled
		self.initd = {'install': {}, 'disable': []}

		# Add a dictionary that can be accessed via info._pluginname for the provider and every plugin
		# Information specific to the module can be added to that 'namespace', this avoids clutter.
		providername = manifest.modules['provider'].__name__.split('.')[-1]
		setattr(self, '_' + providername, {})
		for plugin in manifest.modules['plugins']:
			pluginname = plugin.__name__.split('.')[-1]
			setattr(self, '_' + pluginname, {})

	def __create_manifest_vars(self, manifest, additional_vars={}):
		"""Creates the manifest variables dictionary, based on the manifest contents
		and additional data.

		:param Manifest manifest: The Manifest
		:param dict additional_vars: Additional values (they will take precedence and overwrite anything else)
		:return: The manifest_vars dictionary
		:rtype: dict
		"""
		class DictClass(dict):
			"""Tiny extension of dict to allow setting and getting keys via attributes
			"""
			def __getattr__(self, name):
				return self[name]

			def __setattr__(self, name, value):
				self[name] = value

			def __delattr__(self, name):
				del self[name]

		def set_manifest_vars(obj, data):
			"""Runs through the manifest and creates DictClasses for every key

			:param dict obj: dictionary to set the values on
			:param dict data: dictionary of values to set on the obj
			"""
			for key, value in data.iteritems():
				if isinstance(value, dict):
					obj[key] = DictClass()
					set_manifest_vars(obj[key], value)
					continue
				# Lists are not supported
				if not isinstance(value, list):
					obj[key] = value

		# manifest_vars is a dictionary of all the manifest values,
		# with it users can cross-reference values in the manifest, so that they do not need to be written twice
		manifest_vars = {}
		set_manifest_vars(manifest_vars, manifest.data)

		# Populate the manifest_vars with datetime information
		# and map the datetime variables directly to the dictionary
		from datetime import datetime
		now = datetime.now()
		time_vars = ['%a', '%A', '%b', '%B', '%c', '%d', '%f', '%H',
		             '%I', '%j', '%m', '%M', '%p', '%S', '%U', '%w',
		             '%W', '%x', '%X', '%y', '%Y', '%z', '%Z']
		for key in time_vars:
			manifest_vars[key] = now.strftime(key)

		# Add any additional manifest variables
		# They are added last so that they may override previous variables
		set_manifest_vars(manifest_vars, additional_vars)
		return manifest_vars
