import json


class Manifest(object):
	def __init__(self, path):
		self.path = path
		self.parse(json.load(open(self.path)))

	def parse(self, data):
		self.volume = data['volume']
		self.system = data['system']

	def validate(self):
		pass
