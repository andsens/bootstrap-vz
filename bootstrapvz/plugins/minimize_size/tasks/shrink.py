from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import host
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tools import log_check_call
import os


class AddRequiredCommands(Task):
    description = 'Adding commands required for reducing volume size'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        if info.manifest.plugins['minimize_size'].get('zerofree', False):
            info.host_dependencies['zerofree'] = 'zerofree'
        if info.manifest.plugins['minimize_size'].get('shrink', False):
            link = 'https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation/10_0'
            info.host_dependencies['vmware-vdiskmanager'] = link


class Zerofree(Task):
    description = 'Zeroing unused blocks on the root partition'
    phase = phases.volume_unmounting
    predecessors = [filesystem.UnmountRoot]
    successors = [partitioning.UnmapPartitions, volume.Detach]

    @classmethod
    def run(cls, info):
        log_check_call(['zerofree', info.volume.partition_map.root.device_path])


class ShrinkVolume(Task):
    description = 'Shrinking the volume'
    phase = phases.volume_unmounting
    predecessors = [volume.Detach]

    @classmethod
    def run(cls, info):
        perm = os.stat(info.volume.image_path).st_mode & 0777
        log_check_call(['/usr/bin/vmware-vdiskmanager', '-k', info.volume.image_path])
        os.chmod(info.volume.image_path, perm)
