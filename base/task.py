

class Task(object):
	phase = None
	before = []
	after = []

	def __str__(self):
		return '{module}.{task}'.format(module=self.__module__, task=self.__class__.__name__)

	def __repr__(self):
		return self.__str__()
