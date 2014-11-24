

class CallbackServer(object):

	def __init__(self, listen_port):
		self.listen_port = listen_port

	def start(self, log_server):
		import Pyro4
		self.daemon = Pyro4.Daemon('localhost', port=self.listen_port, unixsocket=None)
		self.daemon.register(log_server)

		def serve():
			self.daemon.requestLoop()
		from threading import Thread
		self.thread = Thread(target=serve)
		self.thread.start()

	def stop(self):
		self.daemon.shutdown()
		self.thread.join()
