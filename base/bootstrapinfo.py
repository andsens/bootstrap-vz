

class BootstrapInformation(object):
	def __init__(self, manifest=None, debug=False):
		self.manifest = manifest
		self.debug = debug

		import random
		self.run_id = '{id:08x}'.format(id=random.randrange(16 ** 8))

		import os.path
		self.workspace = os.path.join(manifest.bootstrapper['workspace'], self.run_id)

		from fs import load_volume
		self.volume = load_volume(self.manifest.volume)

		from pkg.source import SourceLists
		self.source_lists = SourceLists(self.manifest)
		from pkg.package import PackageList
		self.packages = PackageList(self.source_lists, self.manifest)
		self.include_packages = set()
		self.exclude_packages = set()

		self.host_dependencies = set()

		self.initd = {'install': {}, 'disable': []}
