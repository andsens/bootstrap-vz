from build_server import BuildServer
from contextlib import contextmanager


class LocalBuildServer(BuildServer):

    @contextmanager
    def connect(self):
        yield LocalConnection()


class LocalConnection(object):

    def run(self, *args, **kwargs):
        from bootstrapvz.base.main import run
        return run(*args, **kwargs)
