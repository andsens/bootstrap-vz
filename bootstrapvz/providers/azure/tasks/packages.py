from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks.packages import InstallPackages


class DefaultPackages(Task):
    description = 'Adding image packages required for Azure'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('openssl')
        info.packages.add('python-openssl')
        info.packages.add('python-pyasn1')
        info.packages.add('sudo')
        info.packages.add('parted')

        from bootstrapvz.common.tools import config_get, rel_path
        kernel_packages_path = rel_path(__file__, 'packages-kernels.yml')
        kernel_package = config_get(kernel_packages_path, [info.manifest.release.codename,
                                                           info.manifest.system['architecture']])
        info.packages.add(kernel_package)


class Waagent(Task):
    description = 'Add waagent'
    phase = phases.package_installation
    predecessors = [InstallPackages]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        import os
        waagent_version = info.manifest.provider['waagent']['version']
        waagent_file = 'WALinuxAgent-' + waagent_version + '.tar.gz'
        waagent_url = 'https://github.com/Azure/WALinuxAgent/archive/' + waagent_file
        log_check_call(['wget', '-P', info.root, waagent_url])
        waagent_directory = os.path.join(info.root, 'root')
        log_check_call(['tar', 'xaf', os.path.join(info.root, waagent_file), '-C', waagent_directory])
        os.remove(os.path.join(info.root, waagent_file))
        waagent_script = '/root/WALinuxAgent-WALinuxAgent-' + waagent_version + '/waagent'
        log_check_call(['chroot', info.root, 'cp', waagent_script, '/usr/sbin/waagent'])
        log_check_call(['chroot', info.root, 'chmod', '755', '/usr/sbin/waagent'])
        log_check_call(['chroot', info.root, 'waagent', '-install'])
        if info.manifest.provider['waagent'].get('conf', False):
            if os.path.isfile(info.manifest.provider['waagent']['conf']):
                log_check_call(['cp', info.manifest.provider['waagent']['conf'],
                                os.path.join(info.root, 'etc/waagent.conf')])

        # The Azure Linux agent uses 'useradd' to add users, but SHELL
        # is set to /bin/sh by default. Set this to /bin/bash instead.
        from bootstrapvz.common.tools import sed_i
        useradd_config = os.path.join(info.root, 'etc/default/useradd')
        sed_i(useradd_config, r'^(SHELL=.*)', r'SHELL=/bin/bash')
