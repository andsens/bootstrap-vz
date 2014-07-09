import os
from nose.tools import assert_true
from bootstrapvz.base.manifest import Manifest

MANIFEST_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../../manifests'
)


def test_manifest_generator():
    """
    manifests_tests - test_manifest_generator.

    Loops through the manifests directory and tests that
    each file can successfully be loaded and validated.
    """
    for fobj in os.listdir(MANIFEST_DIR):
        path = os.path.join(os.path.abspath(MANIFEST_DIR), fobj)

        yield validate_manifests, path


def validate_manifests(path):
    """
    manifests_tests - validate_manifests.

    Actually creates the manifest for a given path
    and checks that all the data values have successfully
    been created.
    """
    manifest = Manifest(path=path)

    assert_true(manifest.data)
    assert_true(manifest.data['provider'])
    assert_true(manifest.data['bootstrapper'])
    assert_true(manifest.data['image'])
    assert_true(manifest.data['volume'])
    assert_true(manifest.data['system'])
