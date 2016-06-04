from bootstrapvz.base import Task
from bootstrapvz.common import phases


class MoveImage(Task):
    description = 'Moving volume image'
    phase = phases.image_registration

    @classmethod
    def run(cls, info):
        image_name = info.manifest.name.format(**info.manifest_vars)
        filename = image_name + '.' + info.volume.extension

        import os.path
        destination = os.path.join(info.manifest.bootstrapper['workspace'], filename)
        import shutil
        shutil.move(info.volume.image_path, destination)
        info.volume.image_path = destination
        import logging
        log = logging.getLogger(__name__)
        log.info('The volume image has been moved to ' + destination)
