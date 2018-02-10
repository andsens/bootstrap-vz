from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt, bootstrap, dpkg
from . import assets
import os
import shutil


class DpkgUnsafeIo(Task):
    # https://github.com/moby/moby/blob/e2e5d4bc9da5ba17bb2822909611f8300fdd80f0/contrib/mkimage/debootstrap#L94
    description = 'Force dpkg not to call sync()'
    phase = phases.os_installation
    predecessors = [dpkg.CreateDpkgCfg]
    successors = [bootstrap.Bootstrap]

    @classmethod
    def run(cls, info):
        dpkgcfg_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d')

        shutil.copy(
            os.path.join(assets, 'docker-apt-speedup'),
            os.path.join(info.root, dpkgcfg_path, 'docker-apt-speedup'))


class AutoRemoveKernel(Task):
    # https://github.com/moby/moby/blob/e2e5d4bc9da5ba17bb2822909611f8300fdd80f0/contrib/mkimage/debootstrap#L87
    description = 'Do not prevent autoremove of current kernel'
    phase = phases.package_installation
    successors = [apt.AptUpdate]

    @classmethod
    def run(cls, info):
        # this file is one APT creates to make sure we don't "autoremove" our currently
        # in-use kernel, which doesn't really apply to debootstraps/Docker images that
        # don't even have kernels installed
        autoremovekernels = os.path.join(info.root, 'etc/apt/apt.conf.d/01autoremove-kernels')
        if os.path.isfile(autoremovekernels):
            os.remove(autoremovekernels)


class SystemdContainer(Task):
    # https://github.com/systemd/systemd/blob/aa0c34279ee40bce2f9681b496922dedbadfca19/src/basic/virt.c#L434
    description = 'Make systemd-detect-virt return "docker"'
    phase = phases.package_installation
    successors = [apt.AptUpdate]

    @classmethod
    def run(cls, info):
        os.makedirs(os.path.join(info.root, 'run/systemd'))
        with open(os.path.join(info.root, 'run/systemd/container'), 'w') as systemd:
            systemd.write('docker')
