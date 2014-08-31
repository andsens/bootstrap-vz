#!/usr/bin/env python

import random
import Pyro4

# We need to set either a socket communication timeout,
# or use the select based server. Otherwise the daemon requestLoop
# will block indefinitely and is never able to evaluate the loopCondition.
Pyro4.config.COMMTIMEOUT = 0.5

NUM_WORKERS = 5

from ssh_wrapper import RemoteServer
srv = RemoteServer()
srv.start()


class CallbackHandler(object):
	workdone = 0

	def done(self, number):
		print("callback: worker %d reports work is done!" % number)
		CallbackHandler.workdone += 1


class LogServer(object):

	def handle(self, record):
		print('logging' + record)
		# import logging
		# log = logging.getLogger()
		# (handler.handle(record) for handler in log.handlers)


with Pyro4.Daemon('localhost', port=srv.client_port, unixsocket=None) as daemon:
	# register our callback handler
	callback = CallbackHandler()
	daemon.register(callback)
	logger = LogServer()
	daemon.register(logger)

	# contact the server and put it to work

	def serve():
		daemon.requestLoop(loopCondition=lambda: CallbackHandler.workdone < NUM_WORKERS)
	from threading import Thread
	thread = Thread(target=serve)
	thread.start()

	print("creating a bunch of workers")
	with Pyro4.core.Proxy("PYRO:srv@localhost:" + str(srv.server_port)) as server:
		server.set_log_server(logger)
		for _ in range(NUM_WORKERS):
			worker = server.addworker(callback)   # provide our callback handler!
			# worker._pyroOneway.add("work")      # to be able to run in the background
			worker.work(0.5)
		server.stop()

	print("waiting for all work complete...")
	thread.join()
	print("done!")

srv.stop()
