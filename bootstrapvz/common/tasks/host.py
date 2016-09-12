from bootstrapvz.base import Task
from .. import phases
from ..exceptions import TaskError


class CheckExternalCommands(Task):
    description = 'Checking availability of external commands'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        from ..tools import log_check_call
        from subprocess import CalledProcessError
        import re
        missing_packages = []
        for command, package in info.host_dependencies.items():
            try:
                log_check_call(['type', command], shell=True)
            except CalledProcessError:
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
