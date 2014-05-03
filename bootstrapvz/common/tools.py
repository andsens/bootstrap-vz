def log_check_call(command, stdin=None, env=None, shell=False):
	status, stdout, stderr = log_call(command, stdin, env, shell)
	if status != 0:
		from subprocess import CalledProcessError
		raise CalledProcessError(status, ' '.join(command), '\n'.join(stderr))
	return stdout


def log_call(command, stdin=None, env=None, shell=False):
	import subprocess
	import logging
	import Queue
	from multiprocessing.dummy import Pool as ThreadPool
	from os.path import realpath

	command_log = realpath(command[0]).replace('/', '.')
	log = logging.getLogger(__name__ + command_log)
	log.debug('Executing: {command}'.format(command=' '.join(command)))

	process = subprocess.Popen(args=command, env=env, shell=shell,
	                           stdin=subprocess.PIPE,
	                           stdout=subprocess.PIPE,
	                           stderr=subprocess.PIPE)

	def stream_readline(args):
		stream, q = args
		for line in iter(stream.readline, ''):
			q.put((stream, line.strip()))

	if stdin is not None:
		log.debug('  stdin: ' + stdin)
		process.stdin.write(stdin + "\n")
		process.stdin.flush()
	process.stdin.close()

	stdout = []
	stderr = []
	q = Queue.Queue()
	pool = ThreadPool(2)
	pool.map(stream_readline, [(process.stdout, q), (process.stderr, q)])
	pool.close()
	while True:
		try:
			stream, output = q.get_nowait()
			if stream is process.stdout:
				log.debug(output)
				stdout.append(output)
			elif stream is process.stderr:
				log.error(output)
				stderr.append(output)
		except Queue.Empty:
			pool.join()
			process.wait()
			return process.returncode, stdout, stderr


def sed_i(file_path, pattern, subst):
	import fileinput
	import re
	for line in fileinput.input(files=file_path, inplace=True):
		print re.sub(pattern, subst, line),


def load_json(path):
	import json
	from minify_json import json_minify
	with open(path) as stream:
		return json.loads(json_minify(stream.read(), False))


def load_yaml(path):
	import yaml
	with open(path, 'r') as fobj:
		return yaml.safe_load(fobj)


def config_get(path, config_path):
	config = load_json(path)
	for key in config_path:
		config = config.get(key)
	return config


def copy_tree(from_path, to_path):
	from shutil import copy
	import os
	for abs_prefix, dirs, files in os.walk(from_path):
		prefix = os.path.normpath(os.path.relpath(abs_prefix, from_path))
		for path in dirs:
			full_path = os.path.join(to_path, prefix, path)
			if os.path.exists(full_path):
				if os.path.isdir(full_path):
					continue
				else:
					os.remove(full_path)
			os.mkdir(full_path)
		for path in files:
			copy(os.path.join(abs_prefix, path),
			     os.path.join(to_path, prefix, path))
