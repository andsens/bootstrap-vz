

class ManifestError(Exception):
	def __init__(self, message, manifest_path, json_path=None):
		self.message = message
		self.manifest_path = manifest_path
		self.json_path = json_path

	def __str__(self):
		if self.json_path is not None:
			path = '.'.join(map(str, self.json_path))
			return ('{msg}\n  File path: {file}\n  JSON path: {jsonpath}'
			        .format(msg=self.message, file=self.manifest_path, jsonpath=path))
		return '{file}: {msg}'.format(msg=self.message, file=self.manifest_path)


class TaskListError(Exception):
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return 'Error in tasklist: {msg}'.format(msg=self.message)


class TaskError(Exception):
	pass
