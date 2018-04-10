from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import os.path
from . import assets
from . import initd
import shutil


class AddOpenSSHPackage(Task):
    description = 'Adding openssh package'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('openssh-server')


class AddSSHKeyGeneration(Task):
    description = 'Adding SSH private key generation init scripts'
    phase = phases.system_modification
    successors = [initd.InstallInitScripts]

    @classmethod
    def run(cls, info):
        init_scripts_dir = os.path.join(assets, 'init.d')
        systemd_dir = os.path.join(assets, 'systemd')
        install = info.initd['install']
        from subprocess import CalledProcessError
        try:
            log_check_call(['chroot', info.root,
                            'dpkg-query', '-W', 'openssh-server'])
            from bootstrapvz.common.releases import wheezy
            from bootstrapvz.common.releases import jessie
            if info.manifest.release == wheezy:
                install['generate-ssh-hostkeys'] = os.path.join(init_scripts_dir, 'wheezy/generate-ssh-hostkeys')
            elif info.manifest.release == jessie:
                install['generate-ssh-hostkeys'] = os.path.join(init_scripts_dir, 'jessie/generate-ssh-hostkeys')
            else:
                install['ssh-generate-hostkeys'] = os.path.join(init_scripts_dir, 'ssh-generate-hostkeys')

                ssh_keygen_host_service = os.path.join(systemd_dir, 'ssh-generate-hostkeys.service')
                ssh_keygen_host_service_dest = os.path.join(info.root, 'etc/systemd/system/ssh-generate-hostkeys.service')

                ssh_keygen_host_script = os.path.join(assets, 'ssh-generate-hostkeys')
                ssh_keygen_host_script_dest = os.path.join(info.root, 'usr/local/sbin/ssh-generate-hostkeys')

                # Copy files over
                shutil.copy(ssh_keygen_host_service, ssh_keygen_host_service_dest)

                shutil.copy(ssh_keygen_host_script, ssh_keygen_host_script_dest)
                os.chmod(ssh_keygen_host_script_dest, 0o750)

                # Enable systemd service
                log_check_call(['chroot', info.root, 'systemctl', 'enable', 'ssh-generate-hostkeys.service'])

        except CalledProcessError:
            import logging
            logging.getLogger(__name__).warn('The OpenSSH server has not been installed, '
                                             'not installing SSH host key generation script.')


class DisableSSHPasswordAuthentication(Task):
    description = 'Disabling SSH password authentication'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from ..tools import sed_i
        sshd_config_path = os.path.join(info.root, 'etc/ssh/sshd_config')
        sed_i(sshd_config_path, '^#PasswordAuthentication yes', 'PasswordAuthentication no')


class EnableRootLogin(Task):
    description = 'Enabling SSH login for root'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        sshdconfig_path = os.path.join(info.root, 'etc/ssh/sshd_config')
        if os.path.exists(sshdconfig_path):
            from bootstrapvz.common.tools import sed_i
            sed_i(sshdconfig_path, '^#?PermitRootLogin .*', 'PermitRootLogin yes')
        else:
            import logging
            logging.getLogger(__name__).warn('The OpenSSH server has not been installed, '
                                             'not enabling SSH root login.')


class DisableRootLogin(Task):
    description = 'Disabling SSH login for root'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        sshdconfig_path = os.path.join(info.root, 'etc/ssh/sshd_config')
        if os.path.exists(sshdconfig_path):
            from bootstrapvz.common.tools import sed_i
            sed_i(sshdconfig_path, '^#?PermitRootLogin .*', 'PermitRootLogin no')
        else:
            import logging
            logging.getLogger(__name__).warn('The OpenSSH server has not been installed, '
                                             'not disabling SSH root login.')


class DisableSSHDNSLookup(Task):
    description = 'Disabling sshd remote host name lookup'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        sshd_config_path = os.path.join(info.root, 'etc/ssh/sshd_config')
        with open(sshd_config_path, 'a') as sshd_config:
            sshd_config.write('UseDNS no')


class ShredHostkeys(Task):
    description = 'Securely deleting ssh hostkeys'
    phase = phases.system_cleaning

    @classmethod
    def run(cls, info):
        ssh_hostkeys = ['ssh_host_dsa_key',
                        'ssh_host_rsa_key']

        from bootstrapvz.common.releases import wheezy
        if info.manifest.release >= wheezy:
            ssh_hostkeys.append('ssh_host_ecdsa_key')

        from bootstrapvz.common.releases import jessie
        if info.manifest.release >= jessie:
            ssh_hostkeys.append('ssh_host_ed25519_key')

        private = [os.path.join(info.root, 'etc/ssh', name) for name in ssh_hostkeys]
        public = [path + '.pub' for path in private]

        log_check_call(['shred', '--remove'] + [key for key in private + public
                                                if os.path.isfile(key)])
