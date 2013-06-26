

class Phase(object):
	def __init__(self, description):
		self.description = description

	def pos(self):
		from common.phases import order
		return (i for i, phase in enumerate(order) if phase is self).next()

	def __cmp__(self, other):
		return self.pos() - other.pos()

	def __str__(self):
		return '{name}'.format(name=self.__class__.__name__)

	def __repr__(self):
		return self.__str__()
