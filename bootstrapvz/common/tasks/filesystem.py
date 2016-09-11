from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
import bootstrap
import host
import volume


class AddRequiredCommands(Task):
    description = 'Adding commands required for formatting'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        if 'xfs' in (p.filesystem for p in info.volume.partition_map.partitions):
            info.host_dependencies['mkfs.xfs'] = 'xfsprogs'


class Format(Task):
    description = 'Formatting the volume'
    phase = phases.volume_preparation

    @classmethod
    def run(cls, info):
        from bootstrapvz.base.fs.partitions.unformatted import UnformattedPartition
        for partition in info.volume.partition_map.partitions:
            if isinstance(partition, UnformattedPartition):
                continue
            partition.format()


class TuneVolumeFS(Task):
    description = 'Tuning the bootstrap volume filesystem'
    phase = phases.volume_preparation
    predecessors = [Format]

    @classmethod
    def run(cls, info):
        from bootstrapvz.base.fs.partitions.unformatted import UnformattedPartition
        import re
        # Disable the time based filesystem check
        for partition in info.volume.partition_map.partitions:
            if isinstance(partition, UnformattedPartition):
                continue
            if re.match('^ext[2-4]$', partition.filesystem) is not None:
                log_check_call(['tune2fs', '-i', '0', partition.device_path])


class AddXFSProgs(Task):
    description = 'Adding `xfsprogs\' to the image packages'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('xfsprogs')


class CreateMountDir(Task):
    description = 'Creating mountpoint for the root partition'
    phase = phases.volume_mounting

    @classmethod
    def run(cls, info):
        import os
        info.root = os.path.join(info.workspace, 'root')
        os.makedirs(info.root)


class MountRoot(Task):
    description = 'Mounting the root partition'
    phase = phases.volume_mounting
    predecessors = [CreateMountDir]

    @classmethod
    def run(cls, info):
        info.volume.partition_map.root.mount(destination=info.root)


class CreateBootMountDir(Task):
    description = 'Creating mountpoint for the boot partition'
    phase = phases.volume_mounting
    predecessors = [MountRoot]

    @classmethod
    def run(cls, info):
        import os.path
        os.makedirs(os.path.join(info.root, 'boot'))


class MountBoot(Task):
    description = 'Mounting the boot partition'
    phase = phases.volume_mounting
    predecessors = [CreateBootMountDir]

    @classmethod
    def run(cls, info):
        p_map = info.volume.partition_map
        p_map.root.add_mount(p_map.boot, 'boot')


class MountSpecials(Task):
    description = 'Mounting special block devices'
    phase = phases.os_installation
    predecessors = [bootstrap.Bootstrap]

    @classmethod
    def run(cls, info):
        root = info.volume.partition_map.root
        root.add_mount('/dev', 'dev', ['--bind'])
        root.add_mount('none', 'proc', ['--types', 'proc'])
        root.add_mount('none', 'sys', ['--types', 'sysfs'])
        root.add_mount('none', 'dev/pts', ['--types', 'devpts'])


class CopyMountTable(Task):
    description = 'Copying mtab from host system'
    phase = phases.os_installation
    predecessors = [MountSpecials]

    @classmethod
    def run(cls, info):
        import shutil
        import os.path
        shutil.copy('/proc/mounts', os.path.join(info.root, 'etc/mtab'))


class UnmountRoot(Task):
    description = 'Unmounting the bootstrap volume'
    phase = phases.volume_unmounting
    successors = [volume.Detach]

    @classmethod
    def run(cls, info):
        info.volume.partition_map.root.unmount()


class RemoveMountTable(Task):
    description = 'Removing mtab'
    phase = phases.volume_unmounting
    successors = [UnmountRoot]

    @classmethod
    def run(cls, info):
        import os
        os.remove(os.path.join(info.root, 'etc/mtab'))


class DeleteMountDir(Task):
    description = 'Deleting mountpoint for the bootstrap volume'
    phase = phases.volume_unmounting
    predecessors = [UnmountRoot]

    @classmethod
    def run(cls, info):
        import os
        os.rmdir(info.root)
        del info.root


class FStab(Task):
    description = 'Adding partitions to the fstab'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import os.path
        p_map = info.volume.partition_map
        mount_points = [{'path': '/',
                         'partition': p_map.root,
                         'dump': '1',
                         'pass_num': '1',
                         }]
        if hasattr(p_map, 'boot'):
            mount_points.append({'path': '/boot',
                                 'partition': p_map.boot,
                                 'dump': '1',
                                 'pass_num': '2',
                                 })
        if hasattr(p_map, 'swap'):
            mount_points.append({'path': 'none',
                                 'partition': p_map.swap,
                                 'dump': '1',
                                 'pass_num': '0',
                                 })

        fstab_lines = []
        for mount_point in mount_points:
            partition = mount_point['partition']
            mount_opts = ['defaults']
            fstab_lines.append('UUID={uuid} {mountpoint} {filesystem} {mount_opts} {dump} {pass_num}'
                               .format(uuid=partition.get_uuid(),
                                       mountpoint=mount_point['path'],
                                       filesystem=partition.filesystem,
                                       mount_opts=','.join(mount_opts),
                                       dump=mount_point['dump'],
                                       pass_num=mount_point['pass_num']))

        fstab_path = os.path.join(info.root, 'etc/fstab')
        with open(fstab_path, 'w') as fstab:
            fstab.write('\n'.join(fstab_lines))
            fstab.write('\n')
