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
        if isinstance(other, (int, long)):
            return Sectors(self.bytes + self.sector_size * other, self.sector_size)
        if isinstance(other, Bytes):
            return Sectors(self.bytes + other, self.sector_size)
        if isinstance(other, Sectors):
            if self.sector_size != other.sector_size:
                raise UnitError('Cannot sum sectors with different sector sizes')
            return Sectors(self.bytes + other.bytes, self.sector_size)
        raise UnitError('Can only add sectors, bytes or integers to sectors')

    def __iadd__(self, other):
        if isinstance(other, (int, long)):
            self.bytes += self.sector_size * other
            return self
        if isinstance(other, Bytes):
            self.bytes += other
            return self
        if isinstance(other, Sectors):
            if self.sector_size != other.sector_size:
                raise UnitError('Cannot sum sectors with different sector sizes')
            self.bytes += other.bytes
            return self
        raise UnitError('Can only add sectors, bytes or integers to sectors')

    def __sub__(self, other):
        if isinstance(other, (int, long)):
            return Sectors(self.bytes - self.sector_size * other, self.sector_size)
        if isinstance(other, Bytes):
            return Sectors(self.bytes - other, self.sector_size)
        if isinstance(other, Sectors):
            if self.sector_size != other.sector_size:
                raise UnitError('Cannot subtract sectors with different sector sizes')
            return Sectors(self.bytes - other.bytes, self.sector_size)
        raise UnitError('Can only subtract sectors, bytes or integers from sectors')

    def __isub__(self, other):
        if isinstance(other, (int, long)):
            self.bytes -= self.sector_size * other
            return self
        if isinstance(other, Bytes):
            self.bytes -= other
            return self
        if isinstance(other, Sectors):
            if self.sector_size != other.sector_size:
                raise UnitError('Cannot subtract sectors with different sector sizes')
            self.bytes -= other.bytes
            return self
        raise UnitError('Can only subtract sectors, bytes or integers from sectors')

    def __mul__(self, other):
        if isinstance(other, (int, long)):
            return Sectors(self.bytes * other, self.sector_size)
        else:
            raise UnitError('Can only multiply sectors with integers')

    def __imul__(self, other):
        if isinstance(other, (int, long)):
            self.bytes *= other
            return self
        else:
            raise UnitError('Can only multiply sectors with integers')

    def __div__(self, other):
        if isinstance(other, (int, long)):
            return Sectors(self.bytes / other, self.sector_size)
        if isinstance(other, Sectors):
            if self.sector_size == other.sector_size:
                return self.bytes / other.bytes
            else:
                raise UnitError('Cannot divide sectors with different sector sizes')
        raise UnitError('Can only divide sectors with integers or sectors')

    def __idiv__(self, other):
        if isinstance(other, (int, long)):
            self.bytes /= other
            return self
        if isinstance(other, Sectors):
            if self.sector_size == other.sector_size:
                self.bytes /= other.bytes
                return self
            else:
                raise UnitError('Cannot divide sectors with different sector sizes')
        raise UnitError('Can only divide sectors with integers or sectors')

    @onlysectors('Can only take modulus of sectors with sectors')
    def __mod__(self, other):
        if self.sector_size == other.sector_size:
            return Sectors(self.bytes % other.bytes, self.sector_size)
        else:
            raise UnitError('Cannot take modulus of sectors with different sector sizes')

    @onlysectors('Can only take modulus of sectors with sectors')
    def __imod__(self, other):
        if self.sector_size == other.sector_size:
            self.bytes %= other.bytes
            return self
        else:
            raise UnitError('Cannot take modulus of sectors with different sector sizes')

    def __getstate__(self):
        return {'__class__': self.__module__ + '.' + self.__class__.__name__,
                'sector_size': self.sector_size,
                'bytes': self.bytes,
                }

    def __setstate__(self, state):
        self.sector_size = state['sector_size']
        self.bytes = state['bytes']
