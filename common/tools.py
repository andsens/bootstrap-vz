

def log_check_call(command, stdin=None, env=None, shell=False):
	status, stdout, stderr = log_call(command, stdin, env, shell)
	if status != 0:
		from subprocess import CalledProcessError
		raise CalledProcessError(status, ' '.join(command), '\n'.join(stderr))
	return stdout


def log_call(command, stdin=None, env=None, shell=False):
	import subprocess
	import select

	import logging
	from os.path import realpath
	command_log = realpath(command[0]).replace('/', '.')
	log = logging.getLogger(__name__ + command_log)
	log.debug('Executing: {command}'.format(command=' '.join(command)))
	if stdin is not None:
		log.debug('  stdin: {stdin}'.format(stdin=stdin))

	popen_args = {'args':   command,
	              'env':    env,
	              'shell':  shell,
	              'stdin':  subprocess.PIPE,
	              'stdout': subprocess.PIPE,
	              'stderr': subprocess.PIPE, }
	if stdin is not None:
		popen_args['stdin'] = subprocess.PIPE
		process = subprocess.Popen(**popen_args)
		process.stdin.write(stdin + "\n")
		process.stdin.flush()
		process.stdin.close()
	else:
		process = subprocess.Popen(**popen_args)
	stdout = []
	stderr = []
	while True:
		reads = [process.stdout.fileno(), process.stderr.fileno()]
		ret = select.select(reads, [], [])
		for fd in ret[0]:
			if fd == process.stdout.fileno():
				for line in iter(process.stdout.readline, ''):
					log.debug(line.strip())
					stdout.append(line.strip())
			if fd == process.stderr.fileno():
				for line in iter(process.stderr.readline, ''):
					log.error(line.strip())
					stderr.append(line.strip())
		if process.poll() is not None:
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


def config_get(path, config_path):
	config = load_json(path)
	for key in config_path:
		config = config.get(key)
	return config
