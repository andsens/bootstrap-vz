

def get_major_minor_dev_num(device_name):
	import re
	regexp = re.compile('^ *(?P<major>\d+) *(?P<minor>\d+) *(?P<num_blks>\d+) {device_name}$'
	                    .format(device_name=device_name))
	with open('/proc/partitions') as partitions:
		for line in partitions:
			match = regexp.match(line)
			if match is not None:
				return match.group('major'), match.group('minor')
