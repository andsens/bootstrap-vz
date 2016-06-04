from bootstrapvz.base import Task
from bootstrapvz.common import phases


class SetRootPassword(Task):
    description = 'Setting the root password'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root, 'chpasswd'],
                       'root:' + info.manifest.plugins['root_password']['password'])
