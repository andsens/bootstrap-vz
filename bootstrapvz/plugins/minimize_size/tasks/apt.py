from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tools import sed_i
import os
import shutil
from . import assets


class AutomateAptClean(Task):
    description = 'Configuring apt to always clean everything out when it\'s done'
    phase = phases.package_installation
    successors = [apt.AptUpdate]
    # Snatched from:
    # https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

    @classmethod
    def run(cls, info):
        shutil.copy(os.path.join(assets, 'apt-clean'),
                    os.path.join(info.root, 'etc/apt/apt.conf.d/90clean'))


class FilterTranslationFiles(Task):
    description = 'Configuring apt to only download and use specific translation files'
    phase = phases.package_installation
    successors = [apt.AptUpdate]
    # Snatched from:
    # https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

    @classmethod
    def run(cls, info):
        langs = info.manifest.plugins['minimize_size']['apt']['languages']
        config = '; '.join(map(lambda l: '"' + l + '"', langs))
        config_path = os.path.join(info.root, 'etc/apt/apt.conf.d/20languages')
        shutil.copy(os.path.join(assets, 'apt-languages'), config_path)
        sed_i(config_path, r'ACQUIRE_LANGUAGES_FILTER', config)


class AptGzipIndexes(Task):
    description = 'Configuring apt to always gzip lists files'
    phase = phases.package_installation
    successors = [apt.AptUpdate]
    # Snatched from:
    # https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

    @classmethod
    def run(cls, info):
        shutil.copy(os.path.join(assets, 'apt-gzip-indexes'),
                    os.path.join(info.root, 'etc/apt/apt.conf.d/20gzip-indexes'))


class AptAutoremoveSuggests(Task):
    description = 'Configuring apt to remove suggested packages when autoremoving'
    phase = phases.package_installation
    successors = [apt.AptUpdate]
    # Snatched from:
    # https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

    @classmethod
    def run(cls, info):
        shutil.copy(os.path.join(assets, 'apt-autoremove-suggests'),
                    os.path.join(info.root, 'etc/apt/apt.conf.d/20autoremove-suggests'))
