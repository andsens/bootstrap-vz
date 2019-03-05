from __future__ import print_function

from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tools import log_check_call
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import locale
from . import assets
from shutil import copy
import logging
import os


class AddCloudInitPackages(Task):
    description = 'Adding cloud-init package and sudo'
    phase = phases.preparation
    predecessors = [apt.AddBackports]

    @classmethod
    def run(cls, info):
        target = None
        from bootstrapvz.common.releases import wheezy
        if info.manifest.release == wheezy:
            target = '{system.release}-backports'
        info.packages.add('cloud-init', target)
        info.packages.add('sudo')


class SetUsername(Task):
    description = 'Setting username in cloud.cfg'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import sed_i
        cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
        username = info.manifest.plugins['cloud_init']['username']
        search = '^     name: debian$'
        replace = ('     name: {username}\n'
                   '     sudo: ALL=(ALL) NOPASSWD:ALL\n'
                   '     shell: /bin/bash').format(username=username)
        sed_i(cloud_cfg, search, replace)


class SetGroups(Task):
    description = 'Setting groups in cloud.cfg'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import sed_i
        cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
        groups = info.manifest.plugins['cloud_init']['groups']
        search = (r'^     groups: \[adm, audio, cdrom, dialout, floppy, video,'
                  r' plugdev, dip\]$')
        replace = ('     groups: [adm, audio, cdrom, dialout, floppy, video,'
                   ' plugdev, dip, {groups}]').format(groups=', '.join(groups))
        sed_i(cloud_cfg, search, replace)


class SetMetadataSource(Task):
    description = 'Setting metadata source'
    phase = phases.package_installation
    predecessors = [locale.GenerateLocale]
    successors = [apt.AptUpdate]

    @classmethod
    def run(cls, info):
        if 'metadata_sources' in info.manifest.plugins['cloud_init']:
            sources = info.manifest.plugins['cloud_init']['metadata_sources']
        else:
            source_mapping = {'ec2': 'Ec2'}
            sources = source_mapping.get(info.manifest.provider['name'], None)
            if sources is None:
                msg = ('No cloud-init metadata source mapping found for provider `{provider}\', '
                       'skipping selections setting.').format(provider=info.manifest.provider['name'])
                logging.getLogger(__name__).warn(msg)
                return
        sources = "cloud-init    cloud-init/datasources    multiselect    " + sources
        log_check_call(['chroot', info.root, 'debconf-set-selections'], sources)


class DisableModules(Task):
    description = 'Disabling cloud.cfg modules'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import re
        patterns = ""
        for pattern in info.manifest.plugins['cloud_init']['disable_modules']:
            if patterns != "":
                patterns = patterns + "|" + pattern
            else:
                patterns = r"^\s+-\s+(" + pattern
        patterns = patterns + ")$"
        regex = re.compile(patterns)

        cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
        import fileinput
        for line in fileinput.input(files=cloud_cfg, inplace=True):
            if not regex.match(line):
                print(line, end='')


class EnableModules(Task):
    description = 'Enabling cloud.cfg modules'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import fileinput
        import re
        cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
        for section in info.manifest.plugins['cloud_init']['enable_modules']:
            regex = re.compile("^%s:" % section)
            for entry in info.manifest.plugins['cloud_init']['enable_modules'][section]:
                count = 0
                counting = 0
                for line in fileinput.input(files=cloud_cfg, inplace=True):
                    if regex.match(line) and not counting:
                        counting = True
                    if counting:
                        count = count + 1
                    if int(entry['position']) == int(count):
                        print(" - %s" % entry['module'])
                    print(line, end='')


class SetCloudInitMountOptions(Task):
    description = 'Setting cloud-init default mount options'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        cloud_init_src = os.path.join(assets, 'cloud-init/debian_cloud.cfg')
        cloud_init_dst = os.path.join(info.root, 'etc/cloud/cloud.cfg.d/01_debian_cloud.cfg')
        copy(cloud_init_src, cloud_init_dst)
        os.chmod(cloud_init_dst, 0o644)
