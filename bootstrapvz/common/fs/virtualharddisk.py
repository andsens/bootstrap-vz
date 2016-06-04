from qemuvolume import QEMUVolume
from ..tools import log_check_call


class VirtualHardDisk(QEMUVolume):

    extension = 'vhd'
    qemu_format = 'vpc'
    ovf_uri = 'http://go.microsoft.com/fwlink/?LinkId=137171'

    # Azure requires the image size to be a multiple of 1 MiB.
    # VHDs are dynamic by default, so we add the option
    # to make the image size fixed (subformat=fixed)
    def _before_create(self, e):
        self.image_path = e.image_path
        vol_size = str(self.size.bytes.get_qty_in('MiB')) + 'M'
        log_check_call(['qemu-img', 'create', '-o', 'subformat=fixed', '-f', self.qemu_format, self.image_path, vol_size])

    def get_uuid(self):
        if not hasattr(self, 'uuid'):
            import uuid
            self.uuid = uuid.uuid4()
        return self.uuid
