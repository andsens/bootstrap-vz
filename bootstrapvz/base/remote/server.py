

def main():
	opts = getopts()
	log_forwarder = setup_logging()
	serve(opts, log_forwarder)


def setup_logging():
	import logging
	from bootstrapvz.base.log import LogForwarder
	log_forwarder = LogForwarder()
	root = logging.getLogger()
	root.addHandler(log_forwarder)
	root.setLevel(logging.NOTSET)
	return log_forwarder


def serve(opts, log_forwarder):
	class Server(object):

		def __init__(self):
			self.stop_serving = False

		def run(self, *args, **kwargs):
			from bootstrapvz.base.main import run
			return run(*args, **kwargs)

		def set_log_server(self, server):
			return log_forwarder.set_server(server)

		def ping(self):
			return 'pong'

		def stop(self):
			self.stop_serving = True

	import Pyro4
	Pyro4.config.COMMTIMEOUT = 0.5
	daemon = Pyro4.Daemon('localhost', port=int(opts['--listen']), unixsocket=None)

	server = Server()
	daemon.register(server, 'server')
	daemon.requestLoop(loopCondition=lambda: not server.stop_serving)


def getopts():
	from docopt import docopt
	usage = """bootstrap-vz-server

Usage: bootstrap-vz-server [options]

Options:
  --listen <port>    Serve on specified port [default: 46675]
  -h, --help         show this help
"""
	return docopt(usage)
