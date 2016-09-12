from bootstrapvz.base import Task
from bootstrapvz.common import phases
import host
import volume


class AddRequiredCommands(Task):
    description = 'Adding commands required for creating loopback volumes'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        from ..fs.loopbackvolume import LoopbackVolume
        from ..fs.qemuvolume import QEMUVolume
        if type(info.volume) is LoopbackVolume:
            info.host_dependencies['losetup'] = 'mount'
            info.host_dependencies['truncate'] = 'coreutils'
        if isinstance(info.volume, QEMUVolume):
            info.host_dependencies['qemu-img'] = 'qemu-utils'


class Create(Task):
    description = 'Creating a loopback volume'
    phase = phases.volume_creation
    successors = [volume.Attach]

    @classmethod
    def run(cls, info):
        import os.path
        image_path = os.path.join(info.workspace, 'volume.' + info.volume.extension)
        info.volume.create(image_path)
