

class SourceLists(object):

	def __init__(self, manifest_vars):
		self.sources = {}
		self.manifest_vars = manifest_vars

	def add(self, name, line):
		name = name.format(**self.manifest_vars)
		line = line.format(**self.manifest_vars)
		if name not in self.sources:
			self.sources[name] = []
		self.sources[name].append(Source(line))

	def target_exists(self, target):
		target = target.format(**self.manifest_vars)
		for lines in self.sources.itervalues():
			if target in (source.distribution for source in lines):
				return True
		return False


class Source(object):

	def __init__(self, line):
		import re
		regexp = re.compile('^(?P<type>deb|deb-src)\s+'
		                    '(\[\s*(?P<options>.+\S)?\s*\]\s+)?'
		                    '(?P<uri>\S+)\s+'
		                    '(?P<distribution>\S+)'
		                    '(\s+(?P<components>.+\S))?\s*$')
		match = regexp.match(line).groupdict()
		if match is None:
			from exceptions import SourceError
			raise SourceError('Unable to parse source line `{line}\''.format(line=line))
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
		options = ''
		if len(self.options) > 0:
			options = ' [{options}]'.format(options=' '.join(self.options))

		components = ''
		if len(self.components) > 0:
			components = ' {components}'.format(components=' '.join(self.components))

		return ('{type}{options} {uri}'
		        ' {distribution}{components}').format(type=self.type, options=options,
		                                              uri=self.uri, distribution=self.distribution,
		                                              components=components)
