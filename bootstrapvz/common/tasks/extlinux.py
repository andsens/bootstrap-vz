from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import filesystem
import kernel
from bootstrapvz.base.fs import partitionmaps
import os


class AddExtlinuxPackage(Task):
    description = 'Adding extlinux package'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('extlinux')
        if isinstance(info.volume.partition_map, partitionmaps.gpt.GPTPartitionMap):
            info.packages.add('syslinux-common')


class ConfigureExtlinux(Task):
    description = 'Configuring extlinux'
    phase = phases.system_modification
    predecessors = [filesystem.FStab]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.releases import squeeze
        if info.manifest.release == squeeze:
            # On squeeze /etc/default/extlinux is generated when running extlinux-update
            log_check_call(['chroot', info.root,
                            'extlinux-update'])
        from bootstrapvz.common.tools import sed_i
        extlinux_def = os.path.join(info.root, 'etc/default/extlinux')
        sed_i(extlinux_def, r'^EXTLINUX_PARAMETERS="([^"]+)"$',
                            r'EXTLINUX_PARAMETERS="\1 console=ttyS0"')


class InstallExtlinux(Task):
    description = 'Installing extlinux'
    phase = phases.system_modification
    predecessors = [filesystem.FStab, ConfigureExtlinux]

    @classmethod
    def run(cls, info):
        if isinstance(info.volume.partition_map, partitionmaps.gpt.GPTPartitionMap):
            bootloader = '/usr/lib/syslinux/gptmbr.bin'
        else:
            bootloader = '/usr/lib/extlinux/mbr.bin'
        log_check_call(['chroot', info.root,
                        'dd', 'bs=440', 'count=1',
                        'if=' + bootloader,
                        'of=' + info.volume.device_path])
        log_check_call(['chroot', info.root,
                        'extlinux',
                        '--install', '/boot/extlinux'])
        log_check_call(['chroot', info.root,
                        'extlinux-update'])


class ConfigureExtlinuxJessie(Task):
    description = 'Configuring extlinux'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        extlinux_path = os.path.join(info.root, 'boot/extlinux')
        os.mkdir(extlinux_path)

        from . import assets
        with open(os.path.join(assets, 'extlinux/extlinux.conf')) as template:
            extlinux_config_tpl = template.read()

        config_vars = {'root_uuid': info.volume.partition_map.root.get_uuid(),
                       'kernel_version': info.kernel_version}
        # Check if / and /boot are on the same partition
        # If not, /boot will actually be / when booting
        if hasattr(info.volume.partition_map, 'boot'):
            config_vars['boot_prefix'] = ''
        else:
            config_vars['boot_prefix'] = '/boot'

        extlinux_config = extlinux_config_tpl.format(**config_vars)

        with open(os.path.join(extlinux_path, 'extlinux.conf'), 'w') as extlinux_conf_handle:
            extlinux_conf_handle.write(extlinux_config)

        # Copy the boot message
        from shutil import copy
        boot_txt_path = os.path.join(assets, 'extlinux/boot.txt')
        copy(boot_txt_path, os.path.join(extlinux_path, 'boot.txt'))


class InstallExtlinuxJessie(Task):
    description = 'Installing extlinux'
    phase = phases.system_modification
    predecessors = [filesystem.FStab, ConfigureExtlinuxJessie]
    # Make sure the kernel image is updated after we have installed the bootloader
    successors = [kernel.UpdateInitramfs]

    @classmethod
    def run(cls, info):
        if isinstance(info.volume.partition_map, partitionmaps.gpt.GPTPartitionMap):
            # Yeah, somebody saw it fit to uppercase that folder in jessie. Why? BECAUSE
            bootloader = '/usr/lib/EXTLINUX/gptmbr.bin'
        else:
            bootloader = '/usr/lib/EXTLINUX/mbr.bin'
        log_check_call(['chroot', info.root,
                        'dd', 'bs=440', 'count=1',
                        'if=' + bootloader,
                        'of=' + info.volume.device_path])
        log_check_call(['chroot', info.root,
                        'extlinux',
                        '--install', '/boot/extlinux'])
