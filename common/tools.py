

def log_command(command, logger):
	import subprocess
	import select
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	while True:
		reads = [process.stdout.fileno(), process.stderr.fileno()]
		ret = select.select(reads, [], [])
		for fd in ret[0]:
			if fd == process.stdout.fileno():
				line = process.stdout.readline()
				if line != '':
					logger.debug(line.strip())
			if fd == process.stderr.fileno():
				line = process.stderr.readline()
				if line != '':
					logger.error(line.strip())
		if process.poll() is not None:
			break
	return process.returncode


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
