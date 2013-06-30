

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
