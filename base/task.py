

class Task(object):
	phase = None
	predecessors = []
	successors = []

	class __metaclass__(type):
		def __repr__(cls):
			return '{module}.{task}'.format(module=cls.__module__, task=cls.__name__)

		def __str__(cls):
			return repr(cls)

	@classmethod
	def run(cls, info):
		pass
