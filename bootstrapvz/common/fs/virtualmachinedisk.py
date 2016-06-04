from qemuvolume import QEMUVolume


class VirtualMachineDisk(QEMUVolume):

    extension = 'vmdk'
    qemu_format = 'vmdk'
    ovf_uri = 'http://www.vmware.com/specifications/vmdk.html#sparse'

    def get_uuid(self):
        if not hasattr(self, 'uuid'):
            import uuid
            self.uuid = uuid.uuid4()
        return self.uuid
        # import uuid
        # with open(self.image_path) as image:
        #     line = ''
        #     lines_read = 0
        #     while 'ddb.uuid.image="' not in line:
        #         line = image.read()
        #         lines_read += 1
        #         if lines_read > 100:
        #             from common.exceptions import VolumeError
        #             raise VolumeError('Unable to find UUID in VMDK file.')
        #     import re
        #     matches = re.search('ddb.uuid.image="(?P<uuid>[^"]+)"', line)
        #     return uuid.UUID(hex=matches.group('uuid'))
