

# Snatched from here: http://stackoverflow.com/a/7205107
def merge_dicts(*args):
	def merge(a, b, path=None):
		if path is None:
			path = []
		for key in b:
			if key in a:
				if isinstance(a[key], dict) and isinstance(b[key], dict):
					merge(a[key], b[key], path + [str(key)])
				elif a[key] == b[key]:
					pass
				else:
					raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
			else:
						a[key] = b[key]
		return a
	return reduce(merge, args, {})


def bootstrap(manifest, build_settings):
	# if 'build_host' in build_settings:
	# 	run = get_remote_run(build_settings)
	# else:
	# 	run = __import__('bootstrapvz.base.run')
	# run(manifest)
	from ..image import Image
	return Image()


def test_instance(instance, build_settings):
	pass


def get_remote_run(build_settings):
	from ..build.client import SSHRPCServer

	rpc_server = SSHRPCServer(settings)
	try:
		rpc_server.start()
		from time import sleep
		sleep(2)
		log.info('connection to Pyro on remote')
		import Pyro4
		main_uri = 'PYRO:runner@localhost:{local_port}'.format(local_port=rpc_server.local_port)
		main = Pyro4.Proxy(main_uri)
		log.info('running command')
		main.run('eogubhswg')
		log.info('stopping server')
		rpc_server.stop()
	except (Exception, KeyboardInterrupt) as e:
		log.error(e.__class__.__name__ + ': ' + str(e))
	finally:
		print 'cleaning up'
		rpc_server.cleanup()
