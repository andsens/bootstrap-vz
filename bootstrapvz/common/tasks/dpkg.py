from bootstrapvz.base import Task
from bootstrapvz.common.tasks import bootstrap
from .. import phases
import os.path


class CreateDpkgCfg(Task):
    description = 'Creating /etc/dpkg/dpkg.cfg.d before bootstrapping'
    phase = phases.os_installation
    successors = [bootstrap.Bootstrap]

    @classmethod
    def run(cls, info):
        dpkgcfg_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d')
        if not os.path.exists(dpkgcfg_path):
            os.makedirs(dpkgcfg_path)
