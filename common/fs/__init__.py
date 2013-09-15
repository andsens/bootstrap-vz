

def get_partitions():
	import re
	regexp = re.compile('^ *(?P<major>\d+) *(?P<minor>\d+) *(?P<num_blks>\d+) (?P<dev_name>\S+)$')
	matches = {}
	path = '/proc/partitions'
	with open(path) as partitions:
		next(partitions)
		next(partitions)
		for line in partitions:
			match = regexp.match(line)
			if match is None:
				raise RuntimeError('Unable to parse {line} in {path}'.format(line=line, path=path))
			matches[match.group('dev_name')] = match.groupdict()
	return matches
