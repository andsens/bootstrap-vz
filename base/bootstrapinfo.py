

class BootstrapInformation(object):
	def __init__(self, manifest=None, debug=False):
		self.manifest = manifest
		self.debug = debug

		import random
		self.run_id = '{id:08x}'.format(id=random.randrange(16 ** 8))

		import os.path
		self.workspace = os.path.join(manifest.bootstrapper['workspace'], self.run_id)

		from fs import load_volume
		self.volume = load_volume(self.manifest.volume, manifest.system['bootloader'])

		self.apt_mirror = self.manifest.packages.get('mirror', 'http://http.debian.net/debian')

		class DictClass(dict):
			def __getattr__(self, name):
				return self[name]

			def __setattr__(self, name, value):
				self[name] = value

		def set_manifest_vars(obj, data):
			for key, value in data.iteritems():
				if isinstance(value, dict):
					obj[key] = DictClass()
					set_manifest_vars(obj[key], value)
					continue
				if not isinstance(value, list):
					obj[key] = value

		self.manifest_vars = {}
		self.manifest_vars['apt_mirror'] = self.apt_mirror
		set_manifest_vars(self.manifest_vars, self.manifest.data)

		from datetime import datetime
		now = datetime.now()
		time_vars = ['%a', '%A', '%b', '%B', '%c', '%d', '%f', '%H',
		             '%I', '%j', '%m', '%M', '%p', '%S', '%U', '%w',
		             '%W', '%x', '%X', '%y', '%Y', '%z', '%Z']
		for key in time_vars:
			self.manifest_vars[key] = now.strftime(key)

		from pkg.sourceslist import SourceLists
		self.source_lists = SourceLists(self.manifest_vars)
		from pkg.packagelist import PackageList
		self.packages = PackageList(self.manifest_vars, self.source_lists)
		self.include_packages = set()
		self.exclude_packages = set()

		self.host_dependencies = set()

		self.initd = {'install': {}, 'disable': []}
