

class ManifestError(Exception):
	def __init__(self, message, manifest_path, data_path=None):
		self.message = message
		self.manifest_path = manifest_path
		self.data_path = data_path

	def __str__(self):
		if self.data_path is not None:
			path = '.'.join(map(str, self.data_path))
			return ('{msg}\n  File path: {file}\n  Data path: {datapath}'
			        .format(msg=self.message, file=self.manifest_path, datapath=path))
		return '{file}: {msg}'.format(msg=self.message, file=self.manifest_path)


class TaskListError(Exception):
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return 'Error in tasklist: ' + self.message


class TaskError(Exception):
	pass
