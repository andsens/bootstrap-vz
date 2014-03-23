

class Phase(object):
	"""The Phase class represents a phase a task may be in.
	It has no function other than to act as an anchor in the task graph.
	All phases are instantiated in common.phases
	"""
	def __init__(self, name, description):
		# The name of the phase
		self.name = name
		# The description of the phase (currently not used anywhere)
		self.description = description

	def pos(self):
		"""Gets the position of the phase
		Returns:
			int. The positional index of the phase in relation to the other phases
		"""
		from common.phases import order
		return next(i for i, phase in enumerate(order) if phase is self)

	def __cmp__(self, other):
		"""Compares the phase order in relation to the other phases
		"""
		return self.pos() - other.pos()

	def __str__(self):
		"""String representation of the phase, the name suffices

		Returns:
			string.
		"""
		return self.name
