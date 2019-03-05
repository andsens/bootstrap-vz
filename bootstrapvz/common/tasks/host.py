from bootstrapvz.base import Task
from .. import phases
from ..exceptions import TaskError


class CheckExternalCommands(Task):
    description = 'Checking availability of external commands'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        import re
        import os
        import logging
        # https://github.com/PyCQA/pylint/issues/73
        # pylint: disable=no-name-in-module,import-error,useless-suppression
        from distutils.spawn import find_executable
        missing_packages = []
        log = logging.getLogger(__name__)
        for command, package in info.host_dependencies.items():
            log.debug('Checking availability of ' + command)
            path = find_executable(command)
            if path is None or not os.access(path, os.X_OK):
                if re.match(r'^https?:\/\/', package):
                    msg = ('The command `{command}\' is not available, '
                           'you can download the software at `{package}\'.'
                           .format(command=command, package=package))
                else:
                    msg = ('The command `{command}\' is not available, '
                           'it is located in the package `{package}\'.'
                           .format(command=command, package=package))
                missing_packages.append(msg)
        if missing_packages:
            msg = '\n'.join(missing_packages)
            raise TaskError(msg)
