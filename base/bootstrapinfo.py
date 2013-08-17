

class BootstrapInformation(object):
	def __init__(self, manifest=None, debug=False):
		self.manifest = manifest
		self.debug = debug
		import random
		self.run_id = random.randrange(16 ** 8)
