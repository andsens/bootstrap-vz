from exceptions import PackageError


class PackageList(object):

	def __init__(self, sources_list, manifest):
		self.sources_list = sources_list
		self.default_target = manifest.system['release']
		self.remote = {}
		self.local = set()
		if 'remote' in manifest.packages:
			manifest_vars = {'release':      manifest.system['release'],
			                 'architecture': manifest.system['architecture']}
			for package in manifest.packages['remote']:
				target = None
				if isinstance(package, dict):
					name = package['name'].format(**manifest_vars)
					if 'target' in package:
						target = package['target'].format(**manifest_vars)
				else:
					name = package.format(**manifest_vars)
				self.add(name, target)
		if 'local' in manifest.packages:
			for package_path in manifest.packages['local']:
				self.local.add(package_path)

	def add(self, name, target=None):
		if target is None:
			target = self.default_target
		if name in self.remote:
			if self.remote[name] != target:
				msg = ('The package {name} was already added to the package list, '
				       'but with another target release ({target})').format(name=name, target=self.remote[name])
				raise PackageError(msg)
			return

		if not self.sources_list.target_exists(target):
			msg = ('The target release {target} was not found in the sources list').format(target=target)
			raise PackageError(msg)
		self.remote[name] = target
