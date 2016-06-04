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
                record.extra = getattr(record, 'extra', {})
                record.extra['traceback'] = traceback.format_exception(exc_type, exc_value, exc_traceback)
                record.exc_info = None
            # TODO: Use serpent instead
            import pickle
            self.server.handle_log(pickle.dumps(record))
