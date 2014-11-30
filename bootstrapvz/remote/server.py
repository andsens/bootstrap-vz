import Pyro4
import logging

Pyro4.config.REQUIRE_EXPOSE = True
log = logging.getLogger(__name__)


def main():
	opts = getopts()
	from . import register_deserialization_handlers
	register_deserialization_handlers()
	log_forwarder = setup_logging()
	server = Server(opts['--listen'], log_forwarder)
	server.start()


def setup_logging():
	from log import LogForwarder
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

	def __init__(self, listen_port, log_forwarder):
		self.stop_serving = False
		self.log_forwarder = log_forwarder
		self.listen_port = listen_port

	def start(self):
		Pyro4.config.COMMTIMEOUT = 0.5
		daemon = Pyro4.Daemon('localhost', port=int(self.listen_port), unixsocket=None)

		daemon.register(self, 'server')
		daemon.requestLoop(loopCondition=lambda: not self.stop_serving)

	@Pyro4.expose
	def run(self, *args, **kwargs):

		def abort_run():
			return not self.callback_server.get_abort_run()
		from bootstrapvz.base.main import run
		kwargs['check_continue'] = abort_run
		return run(*args, **kwargs)

	@Pyro4.expose
	def set_callback_server(self, server):
		self.callback_server = server
		self.log_forwarder.set_server(self.callback_server)
		log.debug('Forwarding logs to the callback server now')

	@Pyro4.expose
	def ping(self):
		return 'pong'

	@Pyro4.expose
	def stop(self):
		self.stop_serving = True
