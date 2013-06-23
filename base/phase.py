

class Phase(object):
	description = None

	def __init__(self):
		pass

	def __cmp__(self, other):
		from common.phases import order
		return order.index(self) - order.index(other)

	def __str__(self):
		return '{name}'.format(name=self.__class__.__name__)
