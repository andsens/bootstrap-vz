

def main():
	opts = getopts()
	log_forwarder = setup_logging()
	serve(opts, log_forwarder)


def setup_logging():
	import logging
	from log import LogForwarder
	log_forwarder = LogForwarder()
	root = logging.getLogger()
	root.addHandler(log_forwarder)
	root.setLevel(logging.NOTSET)
	return log_forwarder


def serve(opts, log_forwarder):
	class Server(object):

		def run(self, *args, **kwargs):
			from bootstrapvz.base.main import run
			return run(*args, **kwargs)

		def set_log_server(self, server):
			return log_forwarder.set_server(server)

		def ping(self):
			return 'pong'

	server = Server()

	import Pyro4
	daemon = Pyro4.Daemon('localhost', port=int(opts['--listen']), unixsocket=None)
	daemon.register(server, 'server')
	daemon.requestLoop()


def getopts():
	from docopt import docopt
	usage = """bootstrap-vz-server

Usage: bootstrap-vz-server [options]

Options:
  --listen <port>    Serve on specified port [default: 46675]
  -h, --help         show this help
"""
	return docopt(usage)
