

def test_manifest_generator():
    """
    manifests_tests - test_manifest_generator.

    Loops through the manifests directory and tests that
    each file can successfully be loaded and validated.
    """

    from bootstrapvz.base.manifest import Manifest
    from bootstrapvz.base.main import run

    def dry_run(path):
        manifest = Manifest(path=path)
        run(manifest, dry_run=True)

    import os.path
    from .. import recursive_glob
    from itertools import chain
    manifests = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             '../../manifests')
    manifest_paths = chain(recursive_glob(manifests, '*.yml'), recursive_glob(manifests, '*.json'))
    for manifest_path in manifest_paths:
        dry_run.description = "Dry-running %s" % os.path.relpath(manifest_path, manifests)
        yield dry_run, manifest_path
