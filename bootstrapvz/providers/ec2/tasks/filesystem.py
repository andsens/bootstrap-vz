from bootstrapvz.base import Task
from bootstrapvz.common import phases


class S3FStab(Task):
    description = 'Adding the S3 root partition to the fstab'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import os.path
        root = info.volume.partition_map.root

        fstab_lines = []
        mount_opts = ['defaults']
        fstab_lines.append('{device_path}{idx} {mountpoint} {filesystem} {mount_opts} {dump} {pass_num}'
                           .format(device_path='/dev/xvda',
                                   idx=1,
                                   mountpoint='/',
                                   filesystem=root.filesystem,
                                   mount_opts=','.join(mount_opts),
                                   dump='1',
                                   pass_num='1'))

        fstab_path = os.path.join(info.root, 'etc/fstab')
        with open(fstab_path, 'w') as fstab:
            fstab.write('\n'.join(fstab_lines))
            fstab.write('\n')
