

class Task(object):
	name = None

	def __init__(self):
		pass

	def run(self, info):
		print 'Running ' + self.__module__ + "." + self.__class__.__name__
