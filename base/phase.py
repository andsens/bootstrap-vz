from functools import total_ordering

@total_ordering
class Phase(object):
	description = None

	def __init__(self):
		pass

	def __lt__(self, other):
		from common.phases import order
		return order.index(self) < order.index(other)

	def __eq__(self, other):
		return self == other

	def __str__(self):
		return '{name}'.format(name=self.__class__.__name__)
	
	def __repr__(self):
		return self.__str__()
