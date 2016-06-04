

class PackageList(object):
    """Represents a list of packages
    """

    class Remote(object):
        """A remote package with an optional target
        """
        def __init__(self, name, target):
            """
            :param str name: The name of the package
            :param str target: The name of the target release
            """
            self.name = name
            self.target = target

        def __str__(self):
            """Converts the package into somehting that apt-get install can parse

            :rtype: str
            """
            if self.target is None:
                return self.name
            else:
                return self.name + '/' + self.target

    class Local(object):
        """A local package
        """
        def __init__(self, path):
            """
            :param str path: The path to the local package
            """
            self.path = path

        def __str__(self):
            """
            :return: The path to the local package
            :rtype: string
            """
            return self.path

    def __init__(self, manifest_vars, source_lists):
        """
        :param dict manifest_vars: The manifest variables
        :param SourceLists source_lists: The sourcelists for apt
        """
        self.manifest_vars = manifest_vars
        self.source_lists = source_lists
        # The default_target is the release we are bootstrapping
        self.default_target = '{system.release}'.format(**self.manifest_vars)
        # The list of packages that should be installed, this is not a set.
        # We want to preserve the order in which the packages were added so that local
        # packages may be installed in the correct order.
        self.install = []
        # A function that filters the install list and only returns remote packages
        self.remote = lambda: filter(lambda x: isinstance(x, self.Remote), self.install)

    def add(self, name, target=None):
        """Adds a package to the install list

        :param str name: The name of the package to install, may contain manifest vars references
        :param str target: The name of the target release for the package, may contain manifest vars references

        :raises PackageError: When a package of the same name but with a different target has already been added.
        :raises PackageError: When the specified target release could not be found.
        """
        from exceptions import PackageError
        name = name.format(**self.manifest_vars)
        if target is not None:
            target = target.format(**self.manifest_vars)
        # Check if the package has already been added.
        # If so, make sure it's the same target and raise a PackageError otherwise
        package = next((pkg for pkg in self.remote() if pkg.name == name), None)
        if package is not None:
            # It's the same target if the target names match or one of the targets is None
            # and the other is the default target.
            same_target = package.target == target
            same_target = same_target or package.target is None and target == self.default_target
            same_target = same_target or package.target == self.default_target and target is None
            if not same_target:
                msg = ('The package {name} was already added to the package list, '
                       'but with target release `{target}\' instead of `{add_target}\''
                       .format(name=name, target=package.target, add_target=target))
                raise PackageError(msg)
            # The package has already been added, skip the checks below
            return

        # Check if the target exists (unless it's the default target) in the sources list
        # raise a PackageError if does not
        if target not in (None, self.default_target) and not self.source_lists.target_exists(target):
            msg = ('The target release {target} was not found in the sources list').format(target=target)
            raise PackageError(msg)

        # Note that we maintain the target value even if it is none.
        # This allows us to preserve the semantics of the default target when calling apt-get install
        # Why? Try installing nfs-client/wheezy, you can't. It's a virtual package for which you cannot define
        # a target release. Only `apt-get install nfs-client` works.
        self.install.append(self.Remote(name, target))

    def add_local(self, package_path):
        """Adds a local package to the installation list

        :param str package_path: Path to the local package, may contain manifest vars references
        """
        package_path = package_path.format(**self.manifest_vars)
        self.install.append(self.Local(package_path))
