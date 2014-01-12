from exceptions import PackageError


class PackageList(object):

	class Remote(object):
		def __init__(self, name, target):
			self.name = name
			self.target = target

		def __str__(self):
			if self.target is None:
				return self.name
			else:
				return '{name}/{target}'.format(name=self.name, target=self.target)

	class Local(object):
		def __init__(self, path):
			self.path = path

		def __str__(self):
			return self.path

	def __init__(self, manifest_vars, source_lists):
		self.manifest_vars = manifest_vars
		self.source_lists = source_lists
		self.default_target = '{system.release}'.format(**self.manifest_vars)
		self.install = []
		self.remote = lambda: filter(lambda x: isinstance(x, self.Remote), self.install)

	def add(self, name, target=None):
		name = name.format(**self.manifest_vars)
		if target is not None:
			target = target.format(**self.manifest_vars)
		package = next((pkg for pkg in self.remote() if pkg.name == name), None)
		if package is not None:
			same_target = package.target != target
			same_target = same_target or package.target is None and target == self.default_target
			same_target = same_target or package.target == self.default_target and target is None
			if not same_target:
				msg = ('The package {name} was already added to the package list, '
				       'but with another target release ({target})').format(name=name, target=package.target)
				raise PackageError(msg)
			return

		check_target = target
		if check_target is None:
			check_target = self.default_target
		if not self.source_lists.target_exists(check_target):
			msg = ('The target release {target} was not found in the sources list').format(target=check_target)
			raise PackageError(msg)

		self.install.append(self.Remote(name, target))

	def add_local(self, package_path):
		package_path = package_path.format(**self.manifest_vars)
		self.install.append(self.Local(package_path))
