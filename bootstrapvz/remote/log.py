import logging


class LogForwarder(logging.Handler):

	def __init__(self, level=logging.NOTSET):
		self.server = None
		super(LogForwarder, self).__init__(level)

	def set_server(self, server):
		self.server = server

	def emit(self, record):
		if self.server is not None:
			if record.exc_info is not None:
				import traceback
				exc_type, exc_value, exc_traceback = record.exc_info
				record.exc_info = traceback.print_exception(exc_type, exc_value, exc_traceback)
			# TODO: Use serpent instead
			import pickle
			self.server.handle(pickle.dumps(record))


class LogServer(object):

	def handle(self, pickled_record):
		import pickle
		record = pickle.loads(pickled_record)
		log = logging.getLogger()
		record.extra = getattr(record, 'extra', {})
		record.extra['source'] = 'remote'
		log.handle(record)
