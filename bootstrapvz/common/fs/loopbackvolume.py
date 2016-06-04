from bootstrapvz.base.fs.volume import Volume
from ..tools import log_check_call


class LoopbackVolume(Volume):

    extension = 'raw'

    def create(self, image_path):
        self.fsm.create(image_path=image_path)

    def _before_create(self, e):
        self.image_path = e.image_path
        size_opt = '--size={mib}M'.format(mib=self.size.bytes.get_qty_in('MiB'))
        log_check_call(['truncate', size_opt, self.image_path])

    def _before_attach(self, e):
        [self.loop_device_path] = log_check_call(['losetup', '--show', '--find', self.image_path])
        self.device_path = self.loop_device_path

    def _before_detach(self, e):
        log_check_call(['losetup', '--detach', self.loop_device_path])
        del self.loop_device_path
        self.device_path = None

    def _before_delete(self, e):
        from os import remove
        remove(self.image_path)
        del self.image_path
