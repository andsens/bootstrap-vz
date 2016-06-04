

def test_manifest_generator():
    """
    manifests_tests - test_manifest_generator.

    Loops through the manifests directory and tests that
    each file can successfully be loaded and validated.
    """

    from nose.tools import assert_true
    from bootstrapvz.base.manifest import Manifest

    def validate_manifest(path):
        manifest = Manifest(path=path)
        assert_true(manifest.data)
        assert_true(manifest.data['name'])
        assert_true(manifest.data['provider'])
        assert_true(manifest.data['bootstrapper'])
        assert_true(manifest.data['volume'])
        assert_true(manifest.data['system'])

    import os.path
    from .. import recursive_glob
    from itertools import chain
    manifests = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             '../../manifests')
    manifest_paths = chain(recursive_glob(manifests, '*.yml'), recursive_glob(manifests, '*.json'))
    for manifest_path in manifest_paths:
        validate_manifest.description = "Validating %s" % os.path.relpath(manifest_path, manifests)
        yield validate_manifest, manifest_path
