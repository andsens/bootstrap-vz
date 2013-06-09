

def load_manifest(path):
	import json
	return json.load(open(path))


def get_provider(data):
	provider = __import__('providers.{module}'.format(module=data['provider']), fromlist=['providers'])
	return provider


class Manifest(object):
	def __init__(self, path, data):
		self.path = path
		self.parse(data)

	def parse(self, data):
		self.provider = data['provider']
		self.volume   = data['volume']
		self.system   = data['system']
		self.plugins  = data['plugins']

	def validate(self):
		pass

	def load_plugins(self):
		self.loaded_plugins = []
		for modname in self.plugins.keys():
			if self.plugins[modname]['enabled']:
				plugin = __import__('plugins.{module}'.format(module=modname), fromlist=['plugins'])
				self.loaded_plugins.append(plugin)
