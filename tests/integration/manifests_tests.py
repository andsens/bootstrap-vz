from nose.tools import assert_true
from bootstrapvz.base.manifest import Manifest


def test_manifest_generator():
    """
    manifests_tests - test_manifest_generator.

    Loops through the manifests directory and tests that
    each file can successfully be loaded and validated.
    """
    import os.path
    import glob
    manifests = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../../manifests'
    )
    for manifest_path in glob.glob(manifests + '/*.yml'):
        yield validate_manifests, manifest_path
    for manifest_path in glob.glob(manifests + '/*.json'):
        yield validate_manifests, manifest_path


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
