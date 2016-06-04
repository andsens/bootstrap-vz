import Pyro4
import logging

Pyro4.config.REQUIRE_EXPOSE = True
log = logging.getLogger(__name__)


def main():
    opts = getopts()
    from . import register_deserialization_handlers
    register_deserialization_handlers()
    log_forwarder = setup_logging()
    server = Server(opts['--listen'], log_forwarder)
    server.start()


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)

    from log import LogForwarder
    log_forwarder = LogForwarder()
    root.addHandler(log_forwarder)

    from datetime import datetime
    import os.path
    from bootstrapvz.base.log import get_file_handler
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = '{timestamp}_remote.log'.format(timestamp=timestamp)
    logfile_path = os.path.join('/var/log/bootstrap-vz', filename)
    file_handler = get_file_handler(logfile_path, True)
    root.addHandler(file_handler)

    return log_forwarder


def getopts():
    from docopt import docopt
    usage = """bootstrap-vz-server

Usage: bootstrap-vz-server [options]

Options:
  --listen <port>    Serve on specified port [default: 46675]
  -h, --help         show this help
"""
    return docopt(usage)


class Server(object):

    def __init__(self, listen_port, log_forwarder):
        self.stop_serving = False
        self.log_forwarder = log_forwarder
        self.listen_port = listen_port

    def start(self):
        Pyro4.config.COMMTIMEOUT = 0.5
        daemon = Pyro4.Daemon('localhost', port=int(self.listen_port), unixsocket=None)
        daemon.register(self, 'server')

        daemon.requestLoop(loopCondition=lambda: not self.stop_serving)

    @Pyro4.expose
    def set_callback_server(self, server):
        log.debug('Forwarding logs to the callback server')
        self.log_forwarder.set_server(server)

    @Pyro4.expose
    def ping(self):
        if hasattr(self, 'connection_timeout'):
            self.connection_timeout.cancel()
            del self.connection_timeout
        return 'pong'

    @Pyro4.expose
    def stop(self):
        if hasattr(self, 'bootstrap_process'):
            log.warn('Sending SIGINT to bootstrapping process')
            import os
            import signal
            os.killpg(self.bootstrap_process.pid, signal.SIGINT)
            self.bootstrap_process.join()

        # We can't send a SIGINT to the server,
        # for some reason the Pyro4 shutdowns are rather unclean,
        # throwing exceptions and such.
        self.stop_serving = True

    @Pyro4.expose
    def run(self, manifest, debug=False, dry_run=False):

        def bootstrap(queue):
            # setsid() creates a new session, making this process the group leader.
            # We do that, so when the server calls killpg (kill process group)
            # on us, it won't kill itself (this process was spawned from a
            # thread under the server, meaning it's part of the same group).
            # The process hierarchy looks like this:
            # Pyro server (process - listening on a port)
            # +- pool thread
            # +- pool thread
            # +- pool thread
            # +- started thread (the one that got the "run()" call)
            #    L bootstrap() process (us)
            # Calling setsid() also fixes another problem:
            #   SIGINTs sent to this process seem to be redirected
            #   to the process leader. Since there is a thread between
            #   us and the process leader, the signal will not be propagated
            #   (signals are not propagated to threads), this means that any
            #   subprocess we start (i.e. debootstrap) will not get a SIGINT.
            import os
            os.setsid()
            from bootstrapvz.base.main import run
            try:
                bootstrap_info = run(manifest, debug=debug, dry_run=dry_run)
                queue.put(bootstrap_info)
            except (Exception, KeyboardInterrupt) as e:
                queue.put(e)

        from multiprocessing import Queue
        from multiprocessing import Process
        queue = Queue()
        self.bootstrap_process = Process(target=bootstrap, args=(queue,))
        self.bootstrap_process.start()
        self.bootstrap_process.join()
        del self.bootstrap_process
        result = queue.get()
        if isinstance(result, Exception):
            raise result
        return result
