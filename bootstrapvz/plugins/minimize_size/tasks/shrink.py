from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import host
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tools import log_check_call
import os


class AddRequiredZeroFreeCommand(Task):
    description = 'Adding command required for zero-ing volume'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        info.host_dependencies['zerofree'] = 'zerofree'


class AddRequiredVDiskManagerCommand(Task):
    description = 'Adding vmware-vdiskmanager command required for reducing volume size'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        link = 'https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation/10_0'
        info.host_dependencies['vmware-vdiskmanager'] = link


class AddRequiredQemuImgCommand(Task):
    description = 'Adding qemu-img command required for reducing volume size'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        info.host_dependencies['qemu-img'] = 'qemu-img'


class Zerofree(Task):
    description = 'Zeroing unused blocks on the root partition'
    phase = phases.volume_unmounting
    predecessors = [filesystem.UnmountRoot]
    successors = [partitioning.UnmapPartitions, volume.Detach]

    @classmethod
    def run(cls, info):
        log_check_call(['zerofree', info.volume.partition_map.root.device_path])


class ShrinkVolumeWithVDiskManager(Task):
    description = 'Shrinking the volume with vmware-vdiskmanager'
    phase = phases.volume_unmounting
    predecessors = [volume.Detach]

    @classmethod
    def run(cls, info):
        perm = os.stat(info.volume.image_path).st_mode & 0o777
        log_check_call(['/usr/bin/vmware-vdiskmanager', '-k', info.volume.image_path])
        os.chmod(info.volume.image_path, perm)


class ShrinkVolumeWithQemuImg(Task):
    description = 'Shrinking the volume with qemu-img'
    phase = phases.volume_unmounting
    predecessors = [volume.Detach]

    @classmethod
    def run(cls, info):
        tmp_name = os.path.join(info.workspace, 'shrunk.' + info.volume.extension)
        shrink_cmd = ['qemu-img', 'convert', '-O', info.volume.extension, info.volume.image_path, tmp_name]
        # Compress QCOW2 image when shrinking except when explicitly set not to
        if (info.volume.extension == 'qcow2' and
                info.manifest.plugins['minimize_size']['shrink'] != 'qemu-img-no-compression'):
            # '-c' indicates that target image must be compressed (qcow format only)
            shrink_cmd.insert(4, '-c')
        log_check_call(shrink_cmd)
        os.rename(tmp_name, info.volume.image_path)
