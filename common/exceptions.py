__all__ = ['ManifestError']


class ManifestError(Exception):
	def __init__(self, message, manifest):
		self.message = message
		self.manifest = manifest
	def __str__(self):
		return "Error in manifest {0}: {1}".format(self.manifest.path, self.message)


class TaskOrderError(Exception):
	def __init__(self, message, task):
		self.message = message
		self.task = task
	def __str__(self):
		return "Error in task order: {1}".format(self.message)
