from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tools import config_get, rel_path


class DefaultPackages(Task):
    description = 'Adding image packages required for Oracle Compute Cloud'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        kernel_packages_path = rel_path(__file__, 'packages-kernels.yml')
        kernel_package = config_get(kernel_packages_path, [info.manifest.release.codename,
                                                           info.manifest.system['architecture']])
        info.packages.add(kernel_package)
