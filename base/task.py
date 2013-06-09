

class Task(object):
	description = None

	def __init__(self):
		pass

	def run(self, info):
		pass

	def __str__(self):
		return '{module}.{task}'.format(module=self.__module__, task=self.__class__.__name__)
