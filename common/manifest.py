import json


class Manifest(object):
	def __init__(self, path):
		self.path = path
		self.parse(json.load(open(self.path)))

	def parse(self, data):
		self.volume  = data['volume']
		self.system  = data['system']
		self.plugins = data['plugins']

	def validate(self):
		pass

	def load_plugins(self):
		self.loaded_plugins = []
		for modname in self.plugins.keys():
			if self.plugins[modname]['enabled']:
				plugin = __import__('plugins.%s' % modname, fromlist=['plugins'])
				self.loaded_plugins.append(plugin)
