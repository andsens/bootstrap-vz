from bootstrapvz.base import Task
from bootstrapvz.common import phases


class AddPip3Package(Task):
    description = 'Adding `pip\' and Co. to the image packages'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        for package_name in ('build-essential', 'python3-dev', 'python3-pip'):
            info.packages.add(package_name)


class Pip3InstallCommand(Task):
    description = 'Install python packages from pypi with pip'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        packages = info.manifest.plugins['pip3_install']['packages']
        pip_install_command = ['chroot', info.root, 'pip3', 'install']
        pip_install_command.extend(packages)
        log_check_call(pip_install_command)
