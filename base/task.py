

class Task(object):
	name = None

	def __init__(self):
		pass

	def run(self, info):
		pass

	def __str__(self):
		if self.name is None:
			return '{module}.{task}'.format(module=self.__module__, task=self.__class__.__name__)
		else:
			return self.name
