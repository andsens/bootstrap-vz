from base import Task
from common import phases
from common.exceptions import TaskError


class CheckExternalCommands(Task):
	description = 'Checking availability of external commands'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		from common.tools import log_check_call
		from subprocess import CalledProcessError
		missing_packages = []
		for command, package in info.host_dependencies.items():
			try:
				log_check_call(['type ' + command], shell=True)
			except CalledProcessError:
				msg = ('The command `{command}\' is not available, '
				       'it is located in the package `{package}\'.'
				       .format(command=command, package=package))
				missing_packages.append(msg)
		if len(missing_packages) > 0:
			msg = '\n'.join(missing_packages)
			raise TaskError(msg)
