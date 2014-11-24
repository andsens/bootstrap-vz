

class CallbackServer(object):

	def __init__(self, listen_port):
		self.listen_port = listen_port
		self.stop_serving = False

		from log import LogServer
		self.log_server = LogServer()

	def start(self, rpc_server):
		import Pyro4
		Pyro4.config.COMMTIMEOUT = 0.5
		daemon = Pyro4.Daemon('localhost', port=self.listen_port, unixsocket=None)
		daemon.register(self.log_server)

		def serve():
			daemon.requestLoop(loopCondition=lambda: not self.stop_serving)
		from threading import Thread
		self.thread = Thread(target=serve)
		self.thread.start()

		rpc_server.set_log_server(self.log_server)

	def stop(self):
		self.stop_serving = True
		if hasattr(self, 'thread'):
			self.thread.join()
