

class SourceLists(object):
    """Represents a list of sources lists for apt
    """

    def __init__(self, manifest_vars):
        """
        :param dict manifest_vars: The manifest variables
        """
        # A dictionary with the name of the file in sources.list.d as the key
        # That values are lists of Source objects
        self.sources = {}
        # Save the manifest variables, we need the later on
        self.manifest_vars = manifest_vars

    def add(self, name, line):
        """Adds a source to the apt sources list

        :param str name: Name of the file in sources.list.d, may contain manifest vars references
        :param str line: The line for the source file, may contain manifest vars references
        """
        name = name.format(**self.manifest_vars)
        line = line.format(**self.manifest_vars)
        if name not in self.sources:
            self.sources[name] = []
        self.sources[name].append(Source(line))

    def target_exists(self, target):
        """Checks whether the target exists in the sources list

        :param str target: Name of the target to check for, may contain manifest vars references

        :return: Whether the target exists
        :rtype: bool
        """
        target = target.format(**self.manifest_vars)
        # Run through all the sources and return True if the target exists
        for lines in self.sources.itervalues():
            if target in (source.distribution for source in lines):
                return True
        return False


class Source(object):
    """Represents a single source line
    """

    def __init__(self, line):
        """
        :param str line: A apt source line

        :raises SourceError: When the source line cannot be parsed
        """
        # Parse the source line and populate the class attributes with it
        # The format is taken from `man sources.list`
        # or: http://manpages.debian.org/cgi-bin/man.cgi?sektion=5&query=sources.list&apropos=0&manpath=sid&locale=en
        import re
        regexp = re.compile(r'^(?P<type>deb|deb-src)\s+'
                            r'(\[\s*(?P<options>.+\S)?\s*\]\s+)?'
                            r'(?P<uri>\S+)\s+'
                            r'(?P<distribution>\S+)'
                            r'(\s+(?P<components>.+\S))?\s*$')
        match = regexp.match(line).groupdict()
        if match is None:
            from .exceptions import SourceError
            raise SourceError('Unable to parse source line: ' + line)
        self.type = match['type']
        self.options = []
        if match['options'] is not None:
            self.options = re.sub(' +', ' ', match['options']).split(' ')
        self.uri = match['uri']
        self.distribution = match['distribution']
        self.components = []
        if match['components'] is not None:
            self.components = re.sub(' +', ' ', match['components']).split(' ')

    def __str__(self):
        """Convert the object into a source line
        This is pretty much the reverse of what we're doing in the initialization function.

        :rtype: str
        """
        options = ''
        if self.options:
            options = ' [{options}]'.format(options=' '.join(self.options))

        components = ''
        if self.components:
            components = ' {components}'.format(components=' '.join(self.components))

        return ('{type}{options} {uri} {distribution}{components}'
                .format(type=self.type, options=options,
                        uri=self.uri, distribution=self.distribution,
                        components=components))
