from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import network
from bootstrapvz.common.tools import log_check_call


class AddBaselineAptCache(Task):
    description = 'Add a baseline apt cache into the image.'
    phase = phases.system_cleaning
    predecessors = [apt.AptClean]
    successors = [network.RemoveDNSInfo]

    @classmethod
    def run(cls, info):
        log_check_call(['chroot', info.root, 'apt-get', 'update'])
