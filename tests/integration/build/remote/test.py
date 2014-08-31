#!/usr/bin/env python
from remote.ssh_rpc_client import SSHRPCClient

import logging
log = logging.getLogger(__name__)


def main():
	import os.path

	settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'settings.yml'))
	with open(settings_path, 'r') as stream:
		import yaml
		settings = yaml.safe_load(stream)

	bootstrapvz_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../'))
	import sys
	sys.path.append(bootstrapvz_root)

	from bootstrapvz.base.log import get_console_handler
	console_handler = get_console_handler(debug=True)

	root_logger = logging.getLogger()
	root_logger.setLevel(logging.NOTSET)
	root_logger.addHandler(console_handler)

	rpc_server = SSHRPCClient(settings)
	try:
		rpc_server.start_server()
		log.info('connecting to Pyro on remote')
		import Pyro4
		main_uri = 'PYRO:runner@localhost:{local_port}'.format(local_port=rpc_server.local_port)
		main = Pyro4.Proxy(main_uri)
		log.info('running command')
		remaining_retries = 5
		while True:
			try:
				main.run('eogubhswg')
				break
			except Pyro4.errors.ConnectionClosedError as e:
				if remaining_retries > 0:
					remaining_retries -= 1
					from time import sleep
					sleep(2)
				else:
					raise e
		log.info('stopping server')
		rpc_server.stop_server()
	except (Exception, KeyboardInterrupt) as e:
		log.error(e.__class__.__name__ + ': ' + str(e))
	finally:
		print 'cleaning up'
		rpc_server.cleanup()

if __name__ == '__main__':
	main()
