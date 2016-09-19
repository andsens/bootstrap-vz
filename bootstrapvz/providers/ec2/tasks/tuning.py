from bootstrapvz.base import Task
from bootstrapvz.common import phases
from . import assets
from shutil import copy
import os


class TuneSystem(Task):
    description = 'Tuning system for EC2'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        sysctl_src = os.path.join(assets, 'sysctl.d/tuning.conf')
        sysctl_dst = os.path.join(info.root, 'etc/sysctl.d/01_ec2.conf')
        copy(sysctl_src, sysctl_dst)
        os.chmod(sysctl_dst, 0644)


class SetCloudInitMountOptions(Task):
    description = 'Setting cloud-init default mount options'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        cloud_init_src = os.path.join(assets, 'cloud-init/debian_cloud.cfg')
        cloud_init_dst = os.path.join(info.root, 'etc/cloud/cloud.cfg.d/01_debian_cloud.cfg')
        copy(cloud_init_src, cloud_init_dst)
        os.chmod(cloud_init_dst, 0644)


class BlackListModules(Task):
    description = 'Blacklisting unused kernel modules'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        blacklist_path = os.path.join(info.root, 'etc/modprobe.d/blacklist.conf')
        with open(blacklist_path, 'a') as blacklist:
            blacklist.write(('blacklist i2c_piix4\n'
                             'blacklist psmouse\n'))
