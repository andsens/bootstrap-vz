from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import grub
from bootstrapvz.common.tools import rel_path

assets = rel_path(__file__, '../assets')


class SetGrubConsolOutputDeviceToVirtual(Task):
    description = 'Setting the init process terminal output device to `tty0\''
    phase = phases.system_modification
    predecessors = [grub.SetGrubConsolOutputDeviceToSerial]
    successors = [grub.WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_CMDLINE_LINUX'].append('console=tty0')


class SetGrubSystemdShowStatus(Task):
    description = 'Setting systemd show_status'
    phase = phases.system_modification
    successors = [grub.WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_CMDLINE_LINUX'].append('systemd.show_status=1')


class SetSystemdTTYVTDisallocate(Task):
    description = 'Setting systemd TTYVTDisallocate to no\''
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import os.path
        from shutil import copy

        src = os.path.join(assets, 'noclear.conf')
        dst_dir = os.path.join(info.root, 'etc/systemd/system/getty@tty1.service.d')
        dst = os.path.join(dst_dir, 'noclear.conf')
        os.mkdir(dst_dir, 0o755)
        copy(src, dst)
