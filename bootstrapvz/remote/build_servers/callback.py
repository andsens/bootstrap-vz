import Pyro4
import logging

Pyro4.config.REQUIRE_EXPOSE = True
log = logging.getLogger(__name__)


class CallbackServer(object):

    def __init__(self, listen_port, remote_port):
        self.daemon = Pyro4.Daemon(host='localhost', port=listen_port,
                                   nathost='localhost', natport=remote_port,
                                   unixsocket=None)
        self.daemon.register(self)

    def __enter__(self):
        def serve():
            self.daemon.requestLoop()
        from threading import Thread
        self.thread = Thread(target=serve)
        log.debug('Starting callback server')
        self.thread.start()
        return self

    def __exit__(self, type, value, traceback):
        log.debug('Shutting down callback server')
        self.daemon.shutdown()
        self.thread.join()

    @Pyro4.expose
    def handle_log(self, pickled_record):
        import pickle
        record = pickle.loads(pickled_record)
        log = logging.getLogger()
        record.extra = getattr(record, 'extra', {})
        record.extra['source'] = 'remote'
        log.handle(record)
