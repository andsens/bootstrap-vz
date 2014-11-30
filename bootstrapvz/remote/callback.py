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

	def start(self):
		def serve():
			self.daemon.requestLoop()
		from threading import Thread
		self.thread = Thread(target=serve)
		log.debug('Starting the callback server')
		self.thread.start()

	def stop(self):
		if hasattr(self, 'daemon'):
			self.daemon.shutdown()
		if hasattr(self, 'thread'):
			self.thread.join()

	@Pyro4.expose
	def handle_log(self, pickled_record):
		import pickle
		record = pickle.loads(pickled_record)
		log = logging.getLogger()
		record.extra = getattr(record, 'extra', {})
		record.extra['source'] = 'remote'
		log.handle(record)

