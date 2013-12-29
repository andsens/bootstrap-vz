from exceptions import PackageError


class PackageList(object):

	def __init__(self, data, manifest_vars, default_target, source_lists):
		self.manifest_vars = manifest_vars
		self.source_lists = source_lists
		self.default_target = default_target
		self.remote = {}
		self.local = set()
		if 'remote' in data:
			for package in data['remote']:
				target = None
				if isinstance(package, dict):
					name = package['name'].format(**self.manifest_vars)
					if 'target' in package:
						target = package['target'].format(**self.manifest_vars)
				else:
					name = package.format(**self.manifest_vars)
				self.add(name, target)
		if 'local' in data:
			for package_path in data['local']:
				self.local.add(package_path)

	def add(self, name, target=None):
		if target is None:
			target = self.default_target
		name = name.format(**self.manifest_vars)
		target = target.format(**self.manifest_vars)
		if name in self.remote:
			if self.remote[name] != target:
				msg = ('The package {name} was already added to the package list, '
				       'but with another target release ({target})').format(name=name, target=self.remote[name])
				raise PackageError(msg)
			return

		if not self.source_lists.target_exists(target):
			msg = ('The target release {target} was not found in the sources list').format(target=target)
			raise PackageError(msg)
		self.remote[name] = target
