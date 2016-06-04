from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import packages
from bootstrapvz.common.tools import log_check_call
import os


class AddGoogleCloudRepoKey(Task):
    description = 'Adding Google Cloud Repo key.'
    phase = phases.package_installation
    predecessors = [apt.InstallTrustedKeys]
    successors = [apt.WriteSources]

    @classmethod
    def run(cls, info):
        key_file = os.path.join(info.root, 'google.gpg.key')
        log_check_call(['wget', 'https://packages.cloud.google.com/apt/doc/apt-key.gpg', '-O', key_file])
        log_check_call(['chroot', info.root, 'apt-key', 'add', 'google.gpg.key'])
        os.remove(key_file)


class AddGoogleCloudRepoKeyringRepo(Task):
    description = 'Adding Google Cloud keyring repository.'
    phase = phases.preparation
    predecessors = [apt.AddManifestSources]

    @classmethod
    def run(cls, info):
        info.source_lists.add('google-cloud', 'deb http://packages.cloud.google.com/apt google-cloud-packages-archive-keyring-{system.release} main')


class InstallGoogleCloudRepoKeyringPackage(Task):
    description = 'Installing Google Cloud key package.'
    phase = phases.preparation
    successors = [packages.AddManifestPackages]

    @classmethod
    def run(cls, info):
        info.packages.add('google-cloud-packages-archive-keyring')


class CleanupBootstrapRepoKey(Task):
    description = 'Cleaning up bootstrap repo key.'
    phase = phases.system_cleaning

    @classmethod
    def run(cls, info):
        os.remove(os.path.join(info.root, 'etc', 'apt', 'trusted.gpg'))
