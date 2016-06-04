

class _Release(object):
    def __init__(self, codename, version):
        self.codename = codename
        self.version = version

    def __cmp__(self, other):
        return self.version - other.version

    def __str__(self):
        return self.codename

    def __getstate__(self):
        state = self.__dict__.copy()
        state['__class__'] = self.__module__ + '.' + self.__class__.__name__
        return state

    def __setstate__(self, state):
        for key in state:
            self.__dict__[key] = state[key]


class _ReleaseAlias(_Release):
    def __init__(self, alias, release):
        self.alias = alias
        self.release = release
        super(_ReleaseAlias, self).__init__(self.release.codename, self.release.version)

    def __str__(self):
        return self.alias


sid = _Release('sid', 10)
stretch = _Release('stretch', 9)
jessie = _Release('jessie', 8)
wheezy = _Release('wheezy', 7)
squeeze = _Release('squeeze', 6.0)
lenny = _Release('lenny', 5.0)
etch = _Release('etch', 4.0)
sarge = _Release('sarge', 3.1)
woody = _Release('woody', 3.0)
potato = _Release('potato', 2.2)
slink = _Release('slink', 2.1)
hamm = _Release('hamm', 2.0)
bo = _Release('bo', 1.3)
rex = _Release('rex', 1.2)
buzz = _Release('buzz', 1.1)

unstable = _ReleaseAlias('unstable', sid)
testing = _ReleaseAlias('testing', stretch)
stable = _ReleaseAlias('stable', jessie)
oldstable = _ReleaseAlias('oldstable', wheezy)


def get_release(release_name):
    """Normalizes the release codenames
    This allows tasks to query for release codenames rather than 'stable', 'unstable' etc.
    """
    from . import releases
    release = getattr(releases, release_name, None)
    if release is None or not isinstance(release, _Release):
        raise UnknownReleaseException('The release `{name}\' is unknown'.format(name=release))
    return release


class UnknownReleaseException(Exception):
    pass
