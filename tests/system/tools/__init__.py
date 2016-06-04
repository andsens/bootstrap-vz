from contextlib import contextmanager
from bootstrapvz.remote import register_deserialization_handlers
import logging
log = logging.getLogger(__name__)

# Register deserialization handlers for objects
# that will pass between server and client
register_deserialization_handlers()


@contextmanager
def boot_manifest(manifest_data, boot_vars={}):
    from bootstrapvz.common.tools import load_data
    build_servers = load_data('build-servers.yml')
    from bootstrapvz.remote.build_servers import pick_build_server
    build_server = pick_build_server(build_servers, manifest_data)

    manifest_data = build_server.apply_build_settings(manifest_data)
    from bootstrapvz.base.manifest import Manifest
    manifest = Manifest(data=manifest_data)

    import importlib
    provider_module = importlib.import_module('tests.system.providers.' + manifest.provider['name'])

    prepare_bootstrap = getattr(provider_module, 'prepare_bootstrap', noop)
    with prepare_bootstrap(manifest, build_server):
        bootstrap_info = None
        log.info('Connecting to build server')
        with build_server.connect() as connection:
            log.info('Building manifest')
            bootstrap_info = connection.run(manifest)

        log.info('Creating and booting instance')
        with provider_module.boot_image(manifest, build_server, bootstrap_info, **boot_vars) as instance:
            yield instance


def waituntil(predicate, timeout=5, interval=0.05):
    import time
    threshhold = time.time() + timeout
    while time.time() < threshhold:
        if predicate():
            return True
        time.sleep(interval)
    return False


def read_from_socket(socket_path, termination_string, timeout, read_timeout=0.5):
        import socket
        import select
        import errno
        console = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        console.connect(socket_path)
        console.setblocking(0)

        from timeit import default_timer
        start = default_timer()

        output = ''
        ptr = 0
        continue_select = True
        while continue_select:
            read_ready, _, _ = select.select([console], [], [], read_timeout)
            if console in read_ready:
                while True:
                    try:
                        output += console.recv(1024)
                        if termination_string in output[ptr:]:
                            continue_select = False
                        else:
                            ptr = len(output) - len(termination_string)
                        break
                    except socket.error, e:
                        if e.errno != errno.EWOULDBLOCK:
                            raise Exception(e)
                        continue_select = False
            if default_timer() - start > timeout:
                from exceptions import SocketReadTimeout
                msg = ('Reading from socket `{path}\' timed out after {seconds} seconds.\n'
                       'Here is the output so far:\n{output}'
                       .format(path=socket_path, seconds=timeout, output=output))
                raise SocketReadTimeout(msg)
        console.close()
        return output


@contextmanager
def noop(*args, **kwargs):
    yield
