

def log_check_call(command, stdin=None):
	status, stdout, stderr = log_call(command, stdin)
	if status != 0:
		from subprocess import CalledProcessError
		raise CalledProcessError(status, ' '.join(command), '\n'.join(stderr))
	return stdout


def log_call(command, stdin=None):
	import subprocess
	import select

	import logging
	from os.path import realpath
	command_log = realpath(command[0]).replace('/', '.')
	log = logging.getLogger(__name__ + command_log)

	if stdin is not None:
		process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		process.stdin.write(stdin + "\n")
		process.stdin.flush()
		process.stdin.close()
	else:
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
	from tempfile import mkstemp
	from shutil import move
	from os import close
	import os
	import re
	temp_fd, temp_path = mkstemp()
	mode = os.stat(file_path).st_mode
	with open(temp_path, 'w') as new_file:
		with open(file_path) as old_file:
			for line in old_file:
				new_file.write(re.sub(pattern, subst, line))
	close(temp_fd)
	os.chmod(temp_path, mode)
	move(temp_path, file_path)
