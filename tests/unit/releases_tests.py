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
    # "==" tests equality "is" tests identity
    assert releases.stretch == releases.stable
    assert releases.stretch is not releases.stable

    assert releases.stable is releases.stable
    assert releases.stretch is releases.stretch

    assert releases.jessie != releases.stable
    assert releases.jessie is not releases.stable


def test_alias():
    assert releases.oldstable == releases.jessie
    assert releases.stable == releases.stretch
    assert releases.testing == releases.buster
    assert releases.unstable == releases.sid


@raises(releases.UnknownReleaseException)
def test_bogus_releasename():
    releases.get_release('nemo')
