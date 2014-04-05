

class BootstrapInformation(object):
	"""The BootstrapInformation class holds all information about the bootstrapping process.
	The nature of the attributes of this class are rather diverse.
	Tasks may set their own attributes on this class for later retrieval by another task.
	Information that becomes invalid (e.g. a path to a file that has been deleted) must be removed.
	"""
	def __init__(self, manifest=None, debug=False):
		"""Instantiates a new bootstrap info object.

		Args:
			manifest (Manifest): The manifest
			debug (bool): Whether debugging is turned on
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

		# Normalize the release codenames so that tasks may query for release codenames rather than
		# 'stable', 'unstable' etc. This is useful when handling cases that are specific to a release.
		release_codenames_path = os.path.join(os.path.dirname(__file__), 'release-codenames.json')
		from bootstrapvz.common.tools import config_get
		self.release_codename = config_get(release_codenames_path, [self.manifest.system['release']])

		class DictClass(dict):
			"""Tiny extension of dict to allow setting and getting keys via attributes
			"""
			def __getattr__(self, name):
				return self[name]

			def __setattr__(self, name, value):
				self[name] = value

		def set_manifest_vars(obj, data):
			"""Runs through the manifest and creates DictClasses for every key

			Args:
				obj (dict): dictionary to set the values on
				data (dict): dictionary of values to set on the obj
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
		self.manifest_vars = {}
		self.manifest_vars['apt_mirror'] = self.apt_mirror
		set_manifest_vars(self.manifest_vars, self.manifest.data)

		# Populate the manifest_vars with datetime information
		# and map the datetime variables directly to the dictionary
		from datetime import datetime
		now = datetime.now()
		time_vars = ['%a', '%A', '%b', '%B', '%c', '%d', '%f', '%H',
		             '%I', '%j', '%m', '%M', '%p', '%S', '%U', '%w',
		             '%W', '%x', '%X', '%y', '%Y', '%z', '%Z']
		for key in time_vars:
			self.manifest_vars[key] = now.strftime(key)

		# Keep a list of apt sources,
		# so that tasks may add to that list without having to fiddle with apt source list files.
		from pkg.sourceslist import SourceLists
		self.source_lists = SourceLists(self.manifest_vars)
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
