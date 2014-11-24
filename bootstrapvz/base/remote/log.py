import logging
import pickle


class LogForwarder(logging.Handler):

	def __init__(self, level=logging.NOTSET):
		self.server = None
		super(LogForwarder, self).__init__(level)

	def set_server(self, server):
		self.server = server

	def emit(self, record):
		if self.server is not None:
			self.server.handle(pickle.dumps(record))


class LogServer(object):

	def handle(self, pickled_record):
		import logging
		log = logging.getLogger()
		record = pickle.loads(pickled_record)
		log.handle(record)
