from contextlib import contextmanager
import logging
log = logging.getLogger(__name__)


@contextmanager
def boot_image(manifest, build_server, bootstrap_info):
    from bootstrapvz.remote.build_servers.local import LocalBuildServer
    if isinstance(build_server, LocalBuildServer):
        image_path = bootstrap_info.volume.image_path
    else:
        import tempfile
        handle, image_path = tempfile.mkstemp()
        import os
        os.close(handle)
        try:
            build_server.download(bootstrap_info.volume.image_path, image_path)
        except (Exception, KeyboardInterrupt):
            os.remove(image_path)
            raise
        finally:
            build_server.delete(bootstrap_info.volume.image_path)

    from image import VirtualBoxImage
    image = VirtualBoxImage(image_path)

    import hashlib
    image_hash = hashlib.sha1(image_path).hexdigest()
    instance_name = 'bootstrap-vz-{hash}'.format(hash=image_hash[:8])

    try:
        image.open()
        try:
            with run_instance(image, instance_name, manifest) as instance:
                yield instance
        finally:
            image.close()
    finally:
        image.destroy()


@contextmanager
def run_instance(image, instance_name, manifest):
    from instance import VirtualBoxInstance
    instance = VirtualBoxInstance(image, instance_name,
                                  manifest.system['architecture'], manifest.release)
    try:
        instance.create()
        try:
            instance.boot()
            yield instance
        finally:
            instance.shutdown()
    finally:
        instance.destroy()
