from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import grub


class AddVirtualConsoleGrubOutputDevice(Task):
    description = 'Adding `tty0\' as output device for grub'
    phase = phases.system_modification
    successors = [grub.WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_CMDLINE_LINUX_DEFAULT'].append('console=tty0')
