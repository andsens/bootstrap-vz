from qemuvolume import QEMUVolume


class VirtualDiskImage(QEMUVolume):

    extension = 'vdi'
    qemu_format = 'vdi'
    # VDI format does not have an URI (check here: https://forums.virtualbox.org/viewtopic.php?p=275185#p275185)
    ovf_uri = None

    def get_uuid(self):
        import uuid
        with open(self.image_path) as image:
            image.seek(392)
            return uuid.UUID(bytes_le=image.read(16))
