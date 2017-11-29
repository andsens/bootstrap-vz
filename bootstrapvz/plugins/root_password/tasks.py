from bootstrapvz.base import Task
from bootstrapvz.common import phases


class SetRootPassword(Task):
    description = 'Setting the root password'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        password_crypted = info.manifest.plugins['root_password'].get('password-crypted', None)
        if password_crypted is not None:
            log_check_call(['chroot', info.root, '/usr/sbin/chpasswd', '--encrypted'],
                           'root:' + password_crypted)
        else:
            log_check_call(['chroot', info.root, '/usr/sbin/chpasswd'],
                           'root:' + info.manifest.plugins['root_password']['password'])
