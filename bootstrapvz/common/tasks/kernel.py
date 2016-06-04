from bootstrapvz.base import Task
from .. import phases
from ..tasks import packages
import logging


class AddDKMSPackages(Task):
    description = 'Adding DKMS and kernel header packages'
    phase = phases.package_installation
    successors = [packages.InstallPackages]

    @classmethod
    def run(cls, info):
        info.packages.add('dkms')
        kernel_pkg_arch = {'i386': '686-pae', 'amd64': 'amd64'}[info.manifest.system['architecture']]
        info.packages.add('linux-headers-' + kernel_pkg_arch)


class UpdateInitramfs(Task):
    description = 'Rebuilding initramfs'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        # Update initramfs (-u) for all currently installed kernel versions (-k all)
        log_check_call(['chroot', info.root, 'update-initramfs', '-u', '-k', 'all'])


class DetermineKernelVersion(Task):
    description = 'Determining kernel version'
    phase = phases.package_installation
    predecessors = [packages.InstallPackages]

    @classmethod
    def run(cls, info):
        # Snatched from `extlinux-update' in wheezy
        # list the files in boot/ that match vmlinuz-*
        # sort what the * matches, the first entry is the kernel version
        import os.path
        import re
        regexp = re.compile('^vmlinuz-(?P<version>.+)$')

        def get_kernel_version(vmlinuz_path):
            vmlinux_basename = os.path.basename(vmlinuz_path)
            return regexp.match(vmlinux_basename).group('version')
        from glob import glob
        boot = os.path.join(info.root, 'boot')
        vmlinuz_paths = glob('{boot}/vmlinuz-*'.format(boot=boot))
        kernels = map(get_kernel_version, vmlinuz_paths)
        info.kernel_version = sorted(kernels, reverse=True)[0]
        logging.getLogger(__name__).debug('Kernel version is {version}'.format(version=info.kernel_version))
