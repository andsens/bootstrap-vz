from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks.packages import InstallPackages
from bootstrapvz.common.exceptions import TaskError
from bootstrapvz.common.tools import rel_path
import os

assets = rel_path(__file__, '../assets')


class CheckGuestAdditionsPath(Task):
    description = 'Checking whether the VirtualBox Guest Additions image exists'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        guest_additions_path = info.manifest.provider['guest_additions']
        if not os.path.exists(guest_additions_path):
            msg = 'The file {file} does not exist.'.format(file=guest_additions_path)
            raise TaskError(msg)


class AddGuestAdditionsPackages(Task):
    description = 'Adding packages to support Guest Additions installation'
    phase = phases.package_installation
    successors = [InstallPackages]

    @classmethod
    def run(cls, info):
        info.packages.add('bzip2')
        info.packages.add('build-essential')
        info.packages.add('dkms')

        kernel_headers_pkg = 'linux-headers-'
        if info.manifest.system['architecture'] == 'i386':
            arch = 'i686'
            kernel_headers_pkg += '686-pae'
        else:
            arch = 'x86_64'
            kernel_headers_pkg += 'amd64'
        info.packages.add(kernel_headers_pkg)
        info.kernel = {
            'arch': arch,
            'headers_pkg': kernel_headers_pkg,
        }


class InstallGuestAdditions(Task):
    description = 'Installing the VirtualBox Guest Additions'
    phase = phases.package_installation
    predecessors = [InstallPackages]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_call, log_check_call
        for line in log_check_call(['chroot', info.root, 'apt-cache', 'show', info.kernel['headers_pkg']]):
            key, value = line.split(':')
            if key.strip() == 'Depends':
                kernel_version = value.strip().split('linux-headers-')[-1]
                break

        guest_additions_path = info.manifest.provider['guest_additions']
        mount_dir = 'mnt/guest_additions'
        mount_path = os.path.join(info.root, mount_dir)
        os.mkdir(mount_path)
        root = info.volume.partition_map.root
        root.add_mount(guest_additions_path, mount_path, ['-o', 'loop'])
        install_script = os.path.join('/', mount_dir, 'VBoxLinuxAdditions.run')
        install_wrapper_name = 'install_guest_additions.sh'
        install_wrapper = open(os.path.join(assets, install_wrapper_name)) \
            .read() \
            .replace("KERNEL_VERSION", kernel_version) \
            .replace("KERNEL_ARCH", info.kernel['arch']) \
            .replace("INSTALL_SCRIPT", install_script)
        install_wrapper_path = os.path.join(info.root, install_wrapper_name)
        with open(install_wrapper_path, 'w') as f:
            f.write(install_wrapper + '\n')

        # Don't check the return code of the scripts here, because 1 not necessarily means they have failed
        log_call(['chroot', info.root, 'bash', '/' + install_wrapper_name])

        # VBoxService process could be running, as it is not affected by DisableDaemonAutostart
        log_call(['chroot', info.root, 'service', 'vboxadd-service', 'stop'])
        root.remove_mount(mount_path)
        os.rmdir(mount_path)
        os.remove(install_wrapper_path)
