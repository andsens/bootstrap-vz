from bootstrapvz.base.fs.volume import Volume
from bootstrapvz.base.fs.exceptions import VolumeError


class EBSVolume(Volume):

    def create(self, conn, zone):
        self.fsm.create(connection=conn, zone=zone)

    def _before_create(self, e):
        self.conn = e.connection
        zone = e.zone
        size = self.size.bytes.get_qty_in('GiB')
        self.volume = self.conn.create_volume(Size=size,
                                              AvailabilityZone=zone,
                                              VolumeType='gp2')
        self.vol_id = self.volume['VolumeId']
        waiter = self.conn.get_waiter('volume_available')
        waiter.wait(VolumeIds=[self.vol_id],
                    Filters=[{'Name': 'status', 'Values': ['available']}])

    def attach(self, instance_id):
        self.fsm.attach(instance_id=instance_id)

    def _before_attach(self, e):
        import os.path
        import string

        self.instance_id = e.instance_id
        for letter in string.ascii_lowercase[5:]:
            dev_path = os.path.join('/dev', 'xvd' + letter)
            if not os.path.exists(dev_path):
                self.device_path = dev_path
                self.ec2_device_path = os.path.join('/dev', 'sd' + letter)
                break

        if self.device_path is None:
            raise VolumeError('Unable to find a free block device path for mounting the bootstrap volume')

        self.conn.attach_volume(VolumeId=self.vol_id,
                                InstanceId=self.instance_id,
                                Device=self.ec2_device_path)
        waiter = self.conn.get_waiter('volume_in_use')
        waiter.wait(VolumeIds=[self.vol_id],
                    Filters=[{'Name': 'attachment.status', 'Values': ['attached']}])

    def _before_detach(self, e):
        self.conn.detach_volume(VolumeId=self.vol_id,
                                InstanceId=self.instance_id,
                                Device=self.ec2_device_path)
        waiter = self.conn.get_waiter('volume_available')
        waiter.wait(VolumeIds=[self.vol_id],
                    Filters=[{'Name': 'status', 'Values': ['available']}])
        del self.ec2_device_path
        self.device_path = None

    def _before_delete(self, e):
        self.conn.delete_volume(VolumeId=self.vol_id)

    def snapshot(self):
        snapshot = self.conn.create_snapshot(VolumeId=self.vol_id)
        self.snap_id = snapshot['SnapshotId']
        waiter = self.conn.get_waiter('snapshot_completed')
        waiter.wait(SnapshotIds=[self.snap_id],
                    Filters=[{'Name': 'status', 'Values': ['completed']}])
        return self.snap_id
