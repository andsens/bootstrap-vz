from nose.tools import eq_
from nose.tools import raises
from bootstrapvz.common.bytes import Bytes
from bootstrapvz.common.exceptions import UnitError


def test_lt():
    assert Bytes('1MiB') < Bytes('2MiB')


def test_le():
    assert Bytes('1MiB') <= Bytes('2MiB')
    assert Bytes('1MiB') <= Bytes('1MiB')


def test_eq():
    eq_(Bytes('1MiB'), Bytes('1MiB'))


def test_neq():
    assert Bytes('15MiB') != Bytes('1MiB')


def test_gt():
    assert Bytes('2MiB') > Bytes('1MiB')


def test_ge():
    assert Bytes('2MiB') >= Bytes('1MiB')
    assert Bytes('2MiB') >= Bytes('2MiB')


def test_eq_unit():
    eq_(Bytes('1024MiB'), Bytes('1GiB'))


def test_add():
    eq_(Bytes('2GiB'), Bytes('1GiB') + Bytes('1GiB'))


def test_iadd():
    b = Bytes('1GiB')
    b += Bytes('1GiB')
    eq_(Bytes('2GiB'), b)


def test_sub():
    eq_(Bytes('1GiB'), Bytes('2GiB') - Bytes('1GiB'))


def test_isub():
    b = Bytes('2GiB')
    b -= Bytes('1GiB')
    eq_(Bytes('1GiB'), b)


def test_mul():
    eq_(Bytes('2GiB'), Bytes('1GiB') * 2)


@raises(UnitError)
def test_mul_bytes():
    Bytes('1GiB') * Bytes('1GiB')


def test_imul():
    b = Bytes('1GiB')
    b *= 2
    eq_(Bytes('2GiB'), b)


def test_div():
    eq_(Bytes('1GiB'), Bytes('2GiB') / 2)


def test_div_bytes():
    eq_(2, Bytes('2GiB') / Bytes('1GiB'))


def test_idiv():
    b = Bytes('2GiB')
    b /= 2
    eq_(Bytes('1GiB'), b)


def test_mod():
    eq_(Bytes('256MiB'), Bytes('1GiB') % Bytes('768MiB'))


@raises(UnitError)
def test_mod_int():
    Bytes('1GiB') % 768


def test_imod():
    b = Bytes('1GiB')
    b %= Bytes('768MiB')
    eq_(Bytes('256MiB'), b)


@raises(UnitError)
def test_imod_int():
    b = Bytes('1GiB')
    b %= 5


def test_convert_int():
    eq_(pow(1024, 3), int(Bytes('1GiB')))
