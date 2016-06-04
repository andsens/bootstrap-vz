from bootstrapvz.base import Task
from .. import phases
import os.path
from . import assets


class UpdateInitramfs(Task):
    description = 'Updating initramfs'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from ..tools import log_check_call
        log_check_call(['chroot', info.root, 'update-initramfs', '-u'])


class BlackListModules(Task):
    description = 'Blacklisting kernel modules'
    phase = phases.system_modification
    successors = [UpdateInitramfs]

    @classmethod
    def run(cls, info):
        blacklist_path = os.path.join(info.root, 'etc/modprobe.d/blacklist.conf')
        with open(blacklist_path, 'a') as blacklist:
            blacklist.write(('# disable pc speaker and floppy\n'
                             'blacklist pcspkr\n'
                             'blacklist floppy\n'))


class DisableGetTTYs(Task):
    description = 'Disabling getty processes'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        # Forward compatible check for jessie
        from bootstrapvz.common.releases import jessie
        if info.manifest.release < jessie:
            from ..tools import sed_i
            inittab_path = os.path.join(info.root, 'etc/inittab')
            tty1 = '1:2345:respawn:/sbin/getty 38400 tty1'
            sed_i(inittab_path, '^' + tty1, '#' + tty1)
            ttyx = ':23:respawn:/sbin/getty 38400 tty'
            for i in range(2, 7):
                i = str(i)
                sed_i(inittab_path, '^' + i + ttyx + i, '#' + i + ttyx + i)
        else:
            from shutil import copy
            logind_asset_path = os.path.join(assets, 'systemd/logind.conf')
            logind_destination = os.path.join(info.root, 'etc/systemd/logind.conf')
            copy(logind_asset_path, logind_destination)
