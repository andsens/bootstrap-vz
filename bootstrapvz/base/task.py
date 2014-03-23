

class Task(object):
	"""The task class represents are task that can be run.
	It is merely a wrapper for the run function and should never be instantiated.
	"""
	# The phase this task is located in.
	phase = None
	# List of tasks that should run before this task is run
	predecessors = []
	# List of tasks that should run after this task has run
	successors = []

	class __metaclass__(type):
		"""Metaclass to control how the class is coerced into a string
		"""
		def __repr__(cls):
			"""
			Returns:
				string.
			"""
			return '{module}.{task}'.format(module=cls.__module__, task=cls.__name__)

		def __str__(cls):
			"""
			Returns:
				string.
			"""
			return repr(cls)

	@classmethod
	def run(cls, info):
		"""The run function, all work is done inside this function
		Args:
			info (BootstrapInformation): The bootstrap info object
		"""
		pass
