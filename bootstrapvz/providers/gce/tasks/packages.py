from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import packages
from bootstrapvz.common.tools import config_get, rel_path


class DefaultPackages(Task):
    description = 'Adding image packages required for GCE'
    phase = phases.preparation
    successors = [packages.AddManifestPackages]

    @classmethod
    def run(cls, info):
        info.packages.add('acpi-support-base')
        info.packages.add('busybox')
        info.packages.add('ca-certificates')
        info.packages.add('curl')
        info.packages.add('ethtool')
        info.packages.add('gdisk')
        info.packages.add('kpartx')
        info.packages.add('isc-dhcp-client')
        info.packages.add('lsb-release')
        info.packages.add('ntp')
        info.packages.add('parted')
        info.packages.add('python')
        info.packages.add('openssh-client')
        info.packages.add('openssh-server')
        info.packages.add('sudo')
        info.packages.add('uuid-runtime')

        kernel_packages_path = rel_path(__file__, 'packages-kernels.yml')
        kernel_package = config_get(kernel_packages_path, [info.manifest.release.codename,
                                                           info.manifest.system['architecture']])
        info.packages.add(kernel_package)
