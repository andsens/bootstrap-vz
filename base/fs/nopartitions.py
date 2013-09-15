from partitions.singlepartition import SinglePartition


class NoPartitions(object):

	def __init__(self, data):
		root = data['root']
		self.root = SinglePartition(root['size'], root['filesystem'])
		self.partitions = [self.root]
		self.mount_points = [('/', self.root)]

	def get_total_size(self):
		return self.root.size

	def create(self, volume):
		pass

	def map(self, volume):
		pass

	def unmap(self, volume):
		pass

	def format(self):
		self.root.format()

	def mount_root(self, destination):
		self.root.mount(destination)

	def unmount_root(self):
		self.root.unmount()
