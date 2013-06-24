__all__ = ['ManifestError']


class ManifestError(Exception):
	def __init__(self, message, manifest, json_path=None):
		self.message = message
		self.manifest = manifest
		self.json_path = json_path
	def __str__(self):
		if self.json_path is not None:
			path = '.'.join(self.json_path)
			return "{2}\n\tFile: {0}\n\tJSON path: {1}".format(self.manifest.path, path, self.message)
		return "{0}: {1}".format(self.manifest.path, self.message)

class TaskListError(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return "Error in tasklist: {0}".format(self.message)

class VolumeError(Exception):
	pass
