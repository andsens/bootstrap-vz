__all__ = ['ManifestError']


class ManifestError(Exception):
	def __init__(self, message, manifest):
		self.message = message
		self.manifest = manifest
	def __str__(self):
		return "Error in `manifest' {0}: {1}".format(self.manifest.path, self.message)
