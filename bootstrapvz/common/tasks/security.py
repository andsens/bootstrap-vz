from bootstrapvz.base import Task
from .. import phases


class EnableShadowConfig(Task):
    description = 'Enabling shadowconfig'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from ..tools import log_check_call
        log_check_call(['chroot', info.root, 'shadowconfig', 'on'])
