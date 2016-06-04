from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tools import log_check_call


class GatherReleaseInformation(Task):
    description = 'Gathering release information about created image'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        lsb_distribution = log_check_call(['chroot', info.root, 'lsb_release', '-i', '-s'])
        lsb_description = log_check_call(['chroot', info.root, 'lsb_release', '-d', '-s'])
        lsb_release = log_check_call(['chroot', info.root, 'lsb_release', '-r', '-s'])
        info._gce['lsb_distribution'] = lsb_distribution[0]
        info._gce['lsb_description'] = lsb_description[0]
        info._gce['lsb_release'] = lsb_release[0]
