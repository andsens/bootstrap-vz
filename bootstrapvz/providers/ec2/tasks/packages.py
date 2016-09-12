from bootstrapvz.base import Task
from bootstrapvz.common import phases
import os.path


class DefaultPackages(Task):
    description = 'Adding image packages required for EC2'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import rel_path
        info.packages.add('file')  # Needed for the init scripts

        kernel_packages_path = rel_path(__file__, 'packages-kernels.yml')
        from bootstrapvz.common.tools import config_get
        kernel_package = config_get(kernel_packages_path, [info.manifest.release.codename,
                                                           info.manifest.system['architecture']])
        info.packages.add(kernel_package)


class AddWorkaroundGrowpart(Task):
    description = 'Adding growpart workaround for jessie'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from shutil import copy
        from . import assets
        src = os.path.join(assets, 'bin/growpart')
        dst = os.path.join(info.root, 'usr/bin/growpart-workaround')
        copy(src, dst)
