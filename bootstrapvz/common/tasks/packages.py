from bootstrapvz.base import Task
from .. import phases
import apt
from ..tools import log_check_call


class AddManifestPackages(Task):
    description = 'Adding packages from the manifest'
    phase = phases.preparation
    predecessors = [apt.AddManifestSources, apt.AddDefaultSources, apt.AddBackports]

    @classmethod
    def run(cls, info):
        import re
        remote = re.compile('^(?P<name>[^/]+)(/(?P<target>[^/]+))?$')
        for package in info.manifest.packages['install']:
            match = remote.match(package)
            if match is not None:
                info.packages.add(match.group('name'), match.group('target'))
            else:
                info.packages.add_local(package)


class InstallPackages(Task):
    description = 'Installing packages'
    phase = phases.package_installation
    predecessors = [apt.AptUpgrade]

    @classmethod
    def run(cls, info):
        batch = []
        actions = {info.packages.Remote: cls.install_remote,
                   info.packages.Local: cls.install_local}
        for i, package in enumerate(info.packages.install):
            batch.append(package)
            next_package = info.packages.install[i + 1] if i + 1 < len(info.packages.install) else None
            if next_package is None or package.__class__ is not next_package.__class__:
                actions[package.__class__](info, batch)
                batch = []

    @classmethod
    def install_remote(cls, info, remote_packages):
        import os
        from ..tools import log_check_call
        from subprocess import CalledProcessError
        try:
            env = os.environ.copy()
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            log_check_call(['chroot', info.root,
                            'apt-get', 'install',
                                       '--no-install-recommends',
                                       '--assume-yes'] +
                           map(str, remote_packages),
                           env=env)
        except CalledProcessError as e:
            import logging
            disk_stat = os.statvfs(info.root)
            root_free_mb = disk_stat.f_bsize * disk_stat.f_bavail / 1024 / 1024
            disk_stat = os.statvfs(os.path.join(info.root, 'boot'))
            boot_free_mb = disk_stat.f_bsize * disk_stat.f_bavail / 1024 / 1024
            free_mb = min(root_free_mb, boot_free_mb)
            if free_mb < 50:
                msg = ('apt exited with a non-zero status, '
                       'this may be because\nthe image volume is '
                       'running out of disk space ({free}MB left)').format(free=free_mb)
                logging.getLogger(__name__).warn(msg)
            else:
                if e.returncode == 100:
                    msg = ('apt exited with status code 100. '
                           'This can sometimes occur when package retrieval times out or a package extraction failed. '
                           'apt might succeed if you try bootstrapping again.')
                    logging.getLogger(__name__).warn(msg)
            raise

    @classmethod
    def install_local(cls, info, local_packages):
        from shutil import copy
        import os

        absolute_package_paths = []
        chrooted_package_paths = []
        for package_src in local_packages:
            pkg_name = os.path.basename(package_src.path)
            package_rel_dst = os.path.join('tmp', pkg_name)
            package_dst = os.path.join(info.root, package_rel_dst)
            copy(package_src.path, package_dst)
            absolute_package_paths.append(package_dst)
            package_path = os.path.join('/', package_rel_dst)
            chrooted_package_paths.append(package_path)

        env = os.environ.copy()
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        log_check_call(['chroot', info.root,
                        'dpkg', '--install'] + chrooted_package_paths,
                       env=env)

        for path in absolute_package_paths:
            os.remove(path)


class AddTaskselStandardPackages(Task):
    description = 'Adding standard packages from tasksel'
    phase = phases.package_installation
    predecessors = [apt.AptUpdate]
    successors = [InstallPackages]

    @classmethod
    def run(cls, info):
        tasksel_packages = log_check_call(['chroot', info.root, 'tasksel', '--task-packages', 'standard'])
        for pkg in tasksel_packages:
            info.packages.add(pkg)
