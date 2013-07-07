

def log_check_call(command):
	status, stdout, stderr = log_call(command)
	if status != 0:
		from subprocess import CalledProcessError
		raise CalledProcessError(status, ' '.join(command), '\n'.join(stderr))


def log_call(command):
	import subprocess
	import select

	import logging
	from os.path import realpath
	command_log = realpath(command[0]).replace('/', '.')
	log = logging.getLogger(__name__ + command_log)

	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = []
	stderr = []
	while True:
		reads = [process.stdout.fileno(), process.stderr.fileno()]
		ret = select.select(reads, [], [])
		for fd in ret[0]:
			if fd == process.stdout.fileno():
				line = process.stdout.readline()
				if line != '':
					log.debug(line.strip())
					stdout.append(line.strip())
			if fd == process.stderr.fileno():
				line = process.stderr.readline()
				if line != '':
					log.error(line.strip())
					stderr.append(line.strip())
		if process.poll() is not None:
			return process.returncode, stdout, stderr


def sed_i(file_path, pattern, subst):
	from tempfile import mkstemp
	from shutil import move
	from os import close
	temp_fd, temp_path = mkstemp()
	with open(temp_path, 'w') as new_file:
		with open(file_path) as old_file:
			for line in old_file:
				new_file.write(line.replace(pattern, subst))
	close(temp_fd)
	move(temp_path, file_path)
