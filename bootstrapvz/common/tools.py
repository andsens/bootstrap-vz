import os


def log_check_call(command, stdin=None, env=None, shell=False, cwd=None):
	status, stdout, stderr = log_call(command, stdin, env, shell, cwd)
	if status != 0:
		from subprocess import CalledProcessError
		raise CalledProcessError(status, ' '.join(command), '\n'.join(stderr))
	return stdout


def log_call(command, stdin=None, env=None, shell=False, cwd=None):
	import subprocess
	import logging
	from multiprocessing.dummy import Pool as ThreadPool
	from os.path import realpath

	command_log = realpath(command[0]).replace('/', '.')
	log = logging.getLogger(__name__ + command_log)
	log.debug('Executing: {command}'.format(command=' '.join(command)))

	process = subprocess.Popen(args=command, env=env, shell=shell, cwd=cwd,
	                           stdin=subprocess.PIPE,
	                           stdout=subprocess.PIPE,
	                           stderr=subprocess.PIPE)

	if stdin is not None:
		log.debug('  stdin: ' + stdin)
		process.stdin.write(stdin + "\n")
		process.stdin.flush()
	process.stdin.close()

	stdout = []
	stderr = []

	def handle_stdout(line):
		log.debug(line)
		stdout.append(line)

	def handle_stderr(line):
		log.error(line)
		stderr.append(line)

	handlers = {process.stdout: handle_stdout,
	            process.stderr: handle_stderr}

	def stream_readline(stream):
		for line in iter(stream.readline, ''):
			handlers[stream](line.strip())

	pool = ThreadPool(2)
	pool.map(stream_readline, [process.stdout, process.stderr])
	pool.close()
	pool.join()
	process.wait()
	return process.returncode, stdout, stderr


def sed_i(file_path, pattern, subst, expected_replacements=1):
	replacement_count = inline_replace(file_path, pattern, subst)
	if replacement_count < expected_replacements:
		from exceptions import NoMatchesError
		msg = ('There were no matches for the expression `{exp}\' in the file `{path}\''
		       .format(exp=pattern, path=file_path))
		raise NoMatchesError(msg)
	if replacement_count > expected_replacements:
		from exceptions import TooManyMatchesError
		msg = ('There were too many matches for the expression `{exp}\' in the file `{path}\''
		       .format(exp=pattern, path=file_path))
		raise TooManyMatchesError(msg)


def inline_replace(file_path, pattern, subst):
	import fileinput
	import re
	replacement_count = 0
	for line in fileinput.input(files=file_path, inplace=True):
		replacement = re.sub(pattern, subst, line)
		if replacement != line:
			replacement_count += 1
		print replacement,
	return replacement_count


def load_json(path):
	import json
	from minify_json import json_minify
	with open(path) as stream:
		return json.loads(json_minify(stream.read(), False))


def load_yaml(path):
	import yaml
	with open(path, 'r') as stream:
		return yaml.safe_load(stream)


def load_data(path):
	filename, extension = os.path.splitext(path)
	if not os.path.isfile(path):
		raise Exception('The path {path} does not point to a file.'.format(path=path))
	if extension == '.json':
		return load_json(path)
	elif extension == '.yml' or extension == '.yaml':
		return load_yaml(path)
	else:
		raise Exception('Unrecognized extension: {ext}'.format(ext=extension))


def config_get(path, config_path):
	config = load_data(path)
	for key in config_path:
		config = config.get(key)
	return config


def get_codename(release):
	"""Normalizes the release codenames
	This allows tasks to query for release codenames rather than 'stable', 'unstable' etc.
	"""
	release_codenames_path = os.path.join(os.path.dirname(__file__), 'release-codenames.yml')
	from bootstrapvz.common.tools import config_get
	return config_get(release_codenames_path, [release])


def copy_tree(from_path, to_path):
	from shutil import copy
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
