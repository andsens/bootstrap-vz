#!/usr/bin/env python

import time
import Pyro4
import logging
Pyro4.config.COMMTIMEOUT = 5

log = logging.getLogger(__name__)

class Worker(object):
	def __init__(self, number, callback):
		self.number = number
		self.callback = callback
		log.info("Worker %d created" % self.number)

	def work(self, amount):
		print("Worker %d busy..." % self.number)
		time.sleep(amount)
		print("Worker %d done. Informing callback client." % self.number)
		self._pyroDaemon.unregister(self)
		self.callback.done(self.number)  # invoke the callback object


class LogForwarder(logging.Handler):

	def __init__(self, level=logging.NOTSET):
		self.server = None
		super(LogForwarder, self).__init__(level)

	def set_server(self, server):
		self.server = server

	def emit(self, record):
		if self.server is not None:
			self.server.handle('hans')


class CallbackServer(object):

	def __init__(self):
		self.number = 0
		self.serve = True

	def addworker(self, callback):
		self.number += 1
		print("server: adding worker %d" % self.number)
		worker = Worker(self.number, callback)
		self._pyroDaemon.register(worker)   # make it a Pyro object
		return worker

	def stop(self):
		print('called stop()')
		self.serve = False

	def still_serve(self):
		print('called still_serve()')
		return self.serve

	def set_log_server(self, server):
		import logging
		log_forwarder = LogForwarder()
		root = logging.getLogger()
		root.addHandler(log_forwarder)
		root.setLevel(logging.NOTSET)
		log_forwarder.set_server(server)

	def test(self, msg):
		import logging
		root = logging.getLogger()
		root.info(msg)


def main():
	opts = getopts()
	with Pyro4.Daemon('localhost', port=int(opts['--listen-port']), unixsocket=None) as daemon:
		obj = CallbackServer()
		uri = daemon.register(obj, 'srv')
		print uri
		print("Server ready.")
		daemon.requestLoop(loopCondition=lambda: obj.still_serve())


def getopts():
	from docopt import docopt
	usage = """bootstrap-vz-server

Usage: bootstrap-vz-server [options]

Options:
  --listen-port <port>   Serve on specified port [default: 46675]
  --callback-port <port> Connect callback to specified port [default: 46674]
  -h, --help          show this help
"""
	return docopt(usage)

if __name__ == '__main__':
	main()
