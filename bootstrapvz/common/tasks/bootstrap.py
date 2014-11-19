from bootstrapvz.base import Task
from .. import phases
from ..exceptions import TaskError
import host
import logging
import os.path
log = logging.getLogger(__name__)


class AddRequiredCommands(Task):
	description = 'Adding commands required for bootstrapping Debian'
	phase = phases.preparation
	successors = [host.CheckExternalCommands]

	@classmethod
	def run(cls, info):
		info.host_dependencies['debootstrap'] = 'debootstrap'


def get_bootstrap_args(info):
	executable = ['debootstrap']
	arch = info.manifest.system.get('userspace_architecture', info.manifest.system.get('architecture'))
	options = ['--arch=' + arch]
	if len(info.include_packages) > 0:
		options.append('--include=' + ','.join(info.include_packages))
	if len(info.exclude_packages) > 0:
		options.append('--exclude=' + ','.join(info.exclude_packages))
	mirror = info.manifest.bootstrapper.get('mirror', info.apt_mirror)
	arguments = [info.manifest.system['release'], info.root, mirror]
	return executable, options, arguments


def get_tarball_filename(info):
	from hashlib import sha1
	executable, options, arguments = get_bootstrap_args(info)
	# Filter info.root which points at /target/volume-id, we won't ever hit anything with that in there.
	hash_args = [arg for arg in arguments if arg != info.root]
	tarball_id = sha1(repr(frozenset(options + hash_args))).hexdigest()[0:8]
	tarball_filename = 'debootstrap-' + tarball_id + '.tar'
	return os.path.join(info.manifest.bootstrapper['workspace'], tarball_filename)


class MakeTarball(Task):
	description = 'Creating bootstrap tarball'
	phase = phases.os_installation

	@classmethod
	def run(cls, info):
		executable, options, arguments = get_bootstrap_args(info)
		info.tarball = get_tarball_filename(info)
		if os.path.isfile(info.tarball):
			log.debug('Found matching tarball, skipping creation')
		else:
			from ..tools import log_call
			status, out, err = log_call(executable + options + ['--make-tarball=' + info.tarball] + arguments)
			if status != 1:
				msg = 'debootstrap exited with status {status}, it should exit with status 1'.format(status=status)
				raise TaskError(msg)


class Bootstrap(Task):
	description = 'Installing Debian'
	phase = phases.os_installation
	predecessors = [MakeTarball]

	@classmethod
	def run(cls, info):
		executable, options, arguments = get_bootstrap_args(info)
		info.tarball = get_tarball_filename(info)
		if os.path.isfile(info.tarball):
			if not info.manifest.bootstrapper.get('tarball', False):
				# Only shows this message if it hasn't tried to create the tarball
				log.debug('Found matching tarball, skipping download')
			options.extend(['--unpack-tarball=' + info.tarball])

		from ..tools import log_check_call
		log_check_call(executable + options + arguments)


class IncludePackagesInBootstrap(Task):
	description = 'Add packages in the bootstrap phase'
	phase = phases.preparation
	successors = [Bootstrap]

	@classmethod
	def run(cls, info):
		info.include_packages.update(
			set(info.manifest.bootstrapper['include_packages'])
		)


class ExcludePackagesInBootstrap(Task):
	description = 'Remove packages from bootstrap phase'
	phase = phases.preparation
	successors = [Bootstrap]

	@classmethod
	def run(cls, info):
		info.exclude_packages.update(
			set(info.manifest.bootstrapper['exclude_packages'])
		)
