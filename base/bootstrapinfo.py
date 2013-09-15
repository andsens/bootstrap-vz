

class BootstrapInformation(object):
	def __init__(self, manifest=None, debug=False):
		self.manifest = manifest
		from fs import load_volume
		self.volume = load_volume(self.manifest.volume)
		self.debug = debug
		import random
		self.run_id = random.randrange(16 ** 8)
