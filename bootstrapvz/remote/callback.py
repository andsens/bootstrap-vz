import logging
log = logging.getLogger(__name__)


class CallbackServer(object):

	def __init__(self, listen_port, remote_port):
		self.listen_port = listen_port
		self.remote_port = remote_port

	def start(self, log_server):
		import Pyro4
		self.daemon = Pyro4.Daemon(host='localhost', port=self.listen_port,
		                           nathost='localhost', natport=self.remote_port,
		                           unixsocket=None)
		self.daemon.register(log_server)

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
