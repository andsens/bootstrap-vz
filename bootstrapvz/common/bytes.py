

class Bytes(object):

	units = {'B': 1,
	         'KiB': 1024,
	         'MiB': 1024 * 1024,
	         'GiB': 1024 * 1024 * 1024,
	         'TiB': 1024 * 1024 * 1024 * 1024,
	         }

	def __init__(self, qty):
		if isinstance(qty, (int, long)):
			self.qty = qty
		else:
			self.qty = Bytes.parse(qty)

	@staticmethod
	def parse(qty_str):
		import re
		regex = re.compile('^(?P<qty>\d+)(?P<unit>[KMGT]i?B|B)$')
		parsed = regex.match(qty_str)
		if parsed is None:
			raise UnitError('Unable to parse {str}'.format(str=qty_str))

		qty = int(parsed.group('qty'))
		unit = parsed.group('unit')
		if unit[0] in 'KMGT':
			unit = unit[0] + 'iB'
		byte_qty = qty * Bytes.units[unit]
		return byte_qty

	def get_qty_in(self, unit):
		if unit[0] in 'KMGT':
			unit = unit[0] + 'iB'
		if unit not in Bytes.units:
			raise UnitError('Unrecognized unit `{unit}\''.format(unit=Bytes.magnitude))
		if self.qty % Bytes.units[unit] != 0:
			msg = 'Unable to convert {qty} bytes to a whole number in {unit}'.format(qty=self.qty, unit=unit)
			raise UnitError(msg)
		return self.qty / Bytes.units[unit]

	def __repr__(self):
		converted = str(self.get_qty_in('B')) + 'B'
		if self.qty == 0:
			return converted
		for unit in ['TiB', 'GiB', 'MiB', 'KiB']:
			try:
				converted = str(self.get_qty_in(unit)) + unit
				break
			except UnitError:
				pass
		return converted

	def __str__(self):
		return self.__repr__()

	def __int__(self):
		return self.qty

	def __long__(self):
		return self.qty

	def __add__(self, other):
		if not isinstance(other, Bytes):
			raise UnitError('Can only add Bytes to Bytes')
		return Bytes(self.qty + other.qty)

	def __iadd__(self, other):
		if not isinstance(other, Bytes):
			raise UnitError('Can only add Bytes to Bytes')
		self.qty += other.qty
		return self

	def __sub__(self, other):
		if not isinstance(other, Bytes):
			raise UnitError('Can only subtract Bytes from Bytes')
		return Bytes(self.qty - other.qty)

	def __isub__(self, other):
		if not isinstance(other, Bytes):
			raise UnitError('Can only subtract Bytes from Bytes')
		self.qty -= other.qty
		return self

	def __mul__(self, other):
		if not isinstance(other, (int, long)):
			raise UnitError('Can only multiply Bytes with integers')
		return Bytes(self.qty * other)

	def __imul__(self, other):
		if not isinstance(other, (int, long)):
			raise UnitError('Can only multiply Bytes with integers')
		self.qty *= other
		return self

	def __div__(self, other):
		if isinstance(other, Bytes):
			return self.qty / other.qty
		if not isinstance(other, (int, long)):
			raise UnitError('Can only divide Bytes with integers or Bytes')
		return Bytes(self.qty / other)

	def __idiv__(self, other):
		if isinstance(other, Bytes):
			self.qty /= other.qty
		else:
			if not isinstance(other, (int, long)):
				raise UnitError('Can only divide Bytes with integers or Bytes')
			self.qty /= other
		return self

	def __mod__(self, other):
		if isinstance(other, Bytes):
			return self.qty % other.qty
		if not isinstance(other, (int, long)):
			raise UnitError('Can only take modulus of Bytes with integers or Bytes')
		return Bytes(self.qty % other)

	def __imod__(self, other):
		if isinstance(other, Bytes):
			self.qty %= other.qty
		else:
			if not isinstance(other, (int, long)):
				raise UnitError('Can only divide Bytes with integers or Bytes')
			self.qty %= other
		return self


class UnitError(Exception):
	pass
