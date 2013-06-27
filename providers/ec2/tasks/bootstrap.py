from base import Task
from common import phases
from common.exceptions import TaskError
from common.tools import log_command
import logging
log = logging.getLogger(__name__)


def get_bootstrap_args(info):
	executable = ['/usr/sbin/debootstrap']
	options = ['--arch=' + info.manifest.system['architecture']]
	include, exclude = info.img_packages
	if len(include) > 0:
		options.append('--include=' + ','.join(include))
	if len(exclude) > 0:
		options.append('--exclude=' + ','.join(exclude))
	arguments = [info.manifest.system['release'], info.root, 'http://http.debian.net/debian']
	return executable, options, arguments


class MakeTarball(Task):
	description = 'Creating bootstrap tarball'
	phase = phases.os_installation

	def run(self, info):
		from hashlib import sha1
		import os.path
		executable, options, arguments = get_bootstrap_args(info)
		tarball_id = sha1(repr(frozenset(options + arguments))).hexdigest()[0:8]
		tarball_filename = 'debootstrap-{id}.tar'.format(id=tarball_id)
		info.tarball = os.path.join(info.manifest.bootstrapper['tarball_dir'], tarball_filename)

		command = executable + options + ['--make-tarball=' + info.tarball] + arguments
		if log_command(command, log) != 0:
			raise TaskError('Unable to create bootstrap tarball')


class Bootstrap(Task):
	description = 'Installing Debian'
	phase = phases.os_installation
	after = [MakeTarball]

	def run(self, info):
		executable, options, arguments = get_bootstrap_args(info)
		if hasattr(info, 'tarball'):
			options.extend(['--unpack-tarball=' + info.tarball])

		command = executable + options + arguments
		if log_command(command, log) != 0:
			raise TaskError('Unable to bootstrap')
