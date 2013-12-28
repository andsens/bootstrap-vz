

class BootstrapInformation(object):
	def __init__(self, manifest=None, debug=False):
		self.manifest = manifest
		from fs import load_volume
		self.volume = load_volume(self.manifest.volume)
		self.debug = debug
		import random
		self.run_id = '{id:08x}'.format(id=random.randrange(16 ** 8))
		import os.path
		self.workspace = os.path.join(manifest.bootstrapper['workspace'], self.run_id)

		self.initd = {'install': {}, 'disable': []}
