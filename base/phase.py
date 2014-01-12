

class Phase(object):
	def __init__(self, name, description):
		self.name = name
		self.description = description

	def pos(self):
		from common.phases import order
		return next(i for i, phase in enumerate(order) if phase is self)

	def __cmp__(self, other):
		return self.pos() - other.pos()

	def __str__(self):
		return self.name
