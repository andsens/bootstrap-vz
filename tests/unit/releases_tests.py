from nose.tools import raises
from bootstrapvz.common import releases


def test_gt():
    assert releases.wheezy > releases.squeeze


def test_lt():
    assert releases.wheezy < releases.stretch


def test_eq():
    assert releases.wheezy == releases.wheezy


def test_neq():
    assert releases.wheezy != releases.jessie


def test_identity():
    assert releases.wheezy is releases.wheezy


def test_not_identity():
    assert releases.wheezy is not releases.stable
    assert releases.stable is not releases.jessie


def test_alias():
    assert releases.oldstable == releases.wheezy
    assert releases.stable == releases.jessie
    assert releases.testing == releases.stretch
    assert releases.unstable == releases.sid


@raises(releases.UnknownReleaseException)
def test_bogus_releasename():
    releases.get_release('nemo')
