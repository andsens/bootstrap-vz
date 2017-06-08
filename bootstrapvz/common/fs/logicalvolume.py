from bootstrapvz.base.fs.volume import Volume
from bootstrapvz.common.tools import log_check_call
import os


class LogicalVolume(Volume):

    def __init__(self, partitionmap):
        super(LogicalVolume, self).__init__(partitionmap)
        self.vg = ''
        self.lv = ''

    def create(self, volumegroup, logicalvolume):
        self.vg = volumegroup
        self.lv = logicalvolume
        image_path = os.path.join(os.sep, 'dev', self.vg, self.lv)
        self.fsm.create(image_path=image_path)

    def _before_create(self, e):
        self.image_path = e.image_path
        lv_size = str(self.size.bytes.get_qty_in('MiB'))
        log_check_call(['lvcreate', '--size', '{mib}M'.format(mib=lv_size),
                        '--name', self.lv, self.vg])

    def _before_attach(self, e):
        log_check_call(['lvchange', '--activate', 'y', self.image_path])
        [self.loop_device_path] = log_check_call(['losetup', '--show', '--find', '--partscan', self.image_path])
        self.device_path = self.loop_device_path

    def _before_detach(self, e):
        log_check_call(['losetup', '--detach', self.loop_device_path])
        log_check_call(['lvchange', '--activate', 'n', self.image_path])
        del self.loop_device_path
        self.device_path = None

    def delete(self):
        log_check_call(['lvremove', '-f', self.image_path])
        del self.image_path
