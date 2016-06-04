import virtualbox
import logging
log = logging.getLogger(__name__)


class VirtualBoxImage(object):

    def __init__(self, image_path):
        self.image_path = image_path
        self.vbox = virtualbox.VirtualBox()

    def open(self):
        log.debug('Opening vbox medium `{path}\''.format(path=self.image_path))
        self.medium = self.vbox.open_medium(self.image_path,  # location
                                            virtualbox.library.DeviceType.hard_disk,  # device_type
                                            virtualbox.library.AccessMode.read_only,  # access_mode
                                            False)  # force_new_uuid

    def close(self):
        log.debug('Closing vbox medium `{path}\''.format(path=self.image_path))
        self.medium.close()

    def destroy(self):
        log.debug('Deleting vbox image `{path}\''.format(path=self.image_path))
        import os
        os.remove(self.image_path)
        del self.image_path
