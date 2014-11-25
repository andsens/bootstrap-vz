

def main():
	opts = getopts()
	from . import register_deserialization_handlers
	register_deserialization_handlers()
	log_forwarder = setup_logging()
	server = Server(opts, log_forwarder)
	server.start()


def setup_logging():
	import logging
	from bootstrapvz.base.log import LogForwarder
	log_forwarder = LogForwarder()
	root = logging.getLogger()
	root.addHandler(log_forwarder)
	root.setLevel(logging.NOTSET)
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

	def __init__(self, opts, log_forwarder):
		self.stop_serving = False
		self.log_forwarder = log_forwarder
		self.listen_port = opts['--listen']

	def start(self):
		import Pyro4
		Pyro4.config.COMMTIMEOUT = 0.5
		daemon = Pyro4.Daemon('localhost', port=int(self.listen_port), unixsocket=None)

		daemon.register(self, 'server')
		daemon.requestLoop(loopCondition=lambda: not self.stop_serving)

	def run(self, *args, **kwargs):
		from bootstrapvz.base.main import run
		return run(*args, **kwargs)

	def set_log_server(self, server):
		return self.log_forwarder.set_server(server)

	def ping(self):
		return 'pong'

	def stop(self):
		self.stop_serving = True
