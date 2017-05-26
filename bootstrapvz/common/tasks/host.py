from bootstrapvz.base import Task
from .. import phases
from ..exceptions import TaskError


class CheckExternalCommands(Task):
    description = 'Checking availability of external commands'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        import re
        import logging
        from distutils.spawn import find_executable
        missing_packages = []
        log = logging.getLogger(__name__)
        for command, package in info.host_dependencies.items():
            log.debug('Checking availability of ' + command)
            if find_executable(command) is None:
                if re.match('^https?:\/\/', package):
                    msg = ('The command `{command}\' is not available, '
                           'you can download the software at `{package}\'.'
                           .format(command=command, package=package))
                else:
                    msg = ('The command `{command}\' is not available, '
                           'it is located in the package `{package}\'.'
                           .format(command=command, package=package))
                missing_packages.append(msg)
        if len(missing_packages) > 0:
            msg = '\n'.join(missing_packages)
            raise TaskError(msg)
