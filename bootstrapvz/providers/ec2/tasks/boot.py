from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import grub
from . import assets
import os
from bootstrapvz.common.tools import log_check_call


class AddXenGrubConsoleOutputDevice(Task):
    description = 'Adding XEN `hvc0\' as output device for grub'
    phase = phases.system_modification
    successors = [grub.WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_CMDLINE_LINUX_DEFAULT'].append('console=hvc0')


class UpdateGrubConfig(Task):
    description = 'Updating the grub config'
    phase = phases.system_modification
    successors = [grub.WriteGrubConfig]

    @classmethod
    def run(cls, info):
        log_check_call(['chroot', info.root, 'update-grub'])


class CreatePVGrubCustomRule(Task):
    description = 'Creating special rule for PVGrub'
    phase = phases.system_modification
    successors = [UpdateGrubConfig]

    @classmethod
    def run(cls, info):
        import stat
        x_all = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

        grubd = os.path.join(info.root, 'etc/grub.d')
        for cfg in [os.path.join(grubd, f) for f in os.listdir(grubd)]:
            os.chmod(cfg, os.stat(cfg).st_mode & ~ x_all)

        from shutil import copy
        script_src = os.path.join(assets, 'grub.d/40_custom')
        script_dst = os.path.join(info.root, 'etc/grub.d/40_custom')
        copy(script_src, script_dst)
        os.chmod(script_dst, 0o755)

        from bootstrapvz.base.fs.partitionmaps.none import NoPartitions
        if not isinstance(info.volume.partition_map, NoPartitions):
            from bootstrapvz.common.tools import sed_i
            root_idx = info.volume.partition_map.root.get_index()
            grub_device = 'GRUB_DEVICE=/dev/xvda' + str(root_idx)
            sed_i(script_dst, '^GRUB_DEVICE=/dev/xvda$', grub_device)
            grub_root = '\troot (hd0,{idx})'.format(idx=root_idx - 1)
            sed_i(script_dst, '^\troot \\(hd0\\)$', grub_root)

        if info.manifest.volume['backing'] == 's3':
            from bootstrapvz.common.tools import sed_i
            sed_i(script_dst, '^GRUB_DEVICE=/dev/xvda$', 'GRUB_DEVICE=/dev/xvda1')


class ConfigurePVGrub(Task):
    description = 'Configuring PVGrub'
    phase = phases.system_modification
    successors = [UpdateGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_CMDLINE_LINUX'].extend([
            'consoleblank=0',
            'elevator=noop',
        ])


class LinkGrubConfig(Task):
    description = 'Linking the grub config to /boot/grub/menu.lst'
    phase = phases.system_modification
    predecessors = [UpdateGrubConfig]

    @classmethod
    def run(cls, info):
        log_check_call(['chroot', info.root,
                        'ln', '--symbolic', '/boot/grub/grub.cfg', '/boot/grub/menu.lst'])
