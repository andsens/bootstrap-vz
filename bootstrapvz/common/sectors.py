from exceptions import UnitError
from bytes import Bytes


def onlysectors(msg):
	def decorator(func):
		def check_other(self, other):
			if not isinstance(other, Sectors):
				raise UnitError(msg)
			return func(self, other)
		return check_other
	return decorator


class Sectors(object):

	def __init__(self, quantity, sector_size):
		if isinstance(sector_size, Bytes):
			self.sector_size = sector_size
		else:
			self.sector_size = Bytes(sector_size)

		if isinstance(quantity, Bytes):
			self.bytes = quantity
		else:
			if isinstance(quantity, (int, long)):
				self.bytes = self.sector_size * quantity
			else:
				self.bytes = Bytes(quantity)

	def get_sectors(self):
		return self.bytes / self.sector_size

	def __repr__(self):
		return str(self.get_sectors()) + 's'

	def __str__(self):
		return self.__repr__()

	def __int__(self):
		return self.get_sectors()

	def __long__(self):
		return self.get_sectors()

	@onlysectors('Can only compare sectors with sectors')
	def __lt__(self, other):
		return self.bytes < other.bytes

	@onlysectors('Can only compare sectors with sectors')
	def __le__(self, other):
		return self.bytes <= other.bytes

	@onlysectors('Can only compare sectors with sectors')
	def __eq__(self, other):
		return self.bytes == other.bytes

	@onlysectors('Can only compare sectors with sectors')
	def __ne__(self, other):
		return self.bytes != other.bytes

	@onlysectors('Can only compare sectors with sectors')
	def __ge__(self, other):
		return self.bytes >= other.bytes

	@onlysectors('Can only compare sectors with sectors')
	def __gt__(self, other):
		return self.bytes > other.bytes

	def __add__(self, other):
		if not isinstance(other, Sectors):
			raise UnitError('Can only add sectors to sectors')
		if self.sector_size != other.sector_size:
			raise UnitError('Cannot sum sectors with different sector sizes')
		return Sectors(self.bytes + other.bytes, self.sector_size)

	def __iadd__(self, other):
		if not isinstance(other, (Bytes, Sectors)):
			raise UnitError('Can only add Bytes or sectors to sectors')
		if isinstance(other, Bytes):
			self.bytes += other
		if isinstance(other, Sectors):
			if self.sector_size != other.sector_size:
				raise UnitError('Cannot sum sectors with different sector sizes')
			self.bytes += other.bytes
		return self

	def __sub__(self, other):
		if not isinstance(other, (Sectors, int, long)):
			raise UnitError('Can only subtract sectors or integers from sectors')
		if isinstance(other, int):
			return Sectors(self.bytes - self.sector_size * other, self.sector_size)
		else:
			if self.sector_size != other.sector_size:
				raise UnitError('Cannot subtract sectors with different sector sizes')
			return Sectors(self.bytes - other.bytes, self.sector_size)

	def __isub__(self, other):
		if not isinstance(other, (Sectors, int, long)):
			raise UnitError('Can only subtract sectors or integers from sectors')
		if isinstance(other, int):
			self.bytes -= self.sector_size * other
		else:
			if self.sector_size != other.sector_size:
				raise UnitError('Cannot subtract sectors with different sector sizes')
			self.bytes -= other.bytes
		return self

	def __mul__(self, other):
		if not isinstance(other, (int, long)):
			raise UnitError('Can only multiply sectors with integers')
		return Sectors(self.bytes * other, self.sector_size)

	def __imul__(self, other):
		if not isinstance(other, (int, long)):
			raise UnitError('Can only multiply sectors with integers')
		self.bytes *= other
		return self

	def __div__(self, other):
		if isinstance(other, Sectors):
			if self.sector_size != other.sector_size:
				raise UnitError('Cannot divide sectors with different sector sizes')
			return self.bytes / other.bytes
		if not isinstance(other, (int, long)):
			raise UnitError('Can only divide sectors with integers or sectors')
		return Sectors(self.bytes / other, self.sector_size)

	def __idiv__(self, other):
		if isinstance(other, Sectors):
			if self.sector_size != other.sector_size:
				raise UnitError('Cannot divide sectors with different sector sizes')
			self.bytes /= other.bytes
		else:
			if not isinstance(other, (int, long)):
				raise UnitError('Can only divide sectors with integers or sectors')
			self.bytes /= other
		return self

	@onlysectors('Can only take modulus of sectors with sectors')
	def __mod__(self, other):
		if self.sector_size != other.sector_size:
			raise UnitError('Cannot take modulus of sectors with different sector sizes')
		return Sectors(self.bytes % other.bytes, self.sector_size)

	@onlysectors('Can only take modulus of sectors with sectors')
	def __imod__(self, other):
		if self.sector_size != other.sector_size:
			raise UnitError('Cannot take modulus of sectors with different sector sizes')
		self.bytes %= other.bytes
		return self
