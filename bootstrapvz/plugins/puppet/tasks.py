import os
from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.exceptions import TaskError
from bootstrapvz.common.releases import jessie, wheezy, stretch
from bootstrapvz.common.tools import sed_i, log_check_call, rel_path


ASSETS_DIR_STRETCH = rel_path(__file__, 'assets/gpg-keyrings-PC1/stretch')
ASSETS_DIR_JESSIE = rel_path(__file__, 'assets/gpg-keyrings-PC1/jessie')
ASSETS_DIR_WHEEZY = rel_path(__file__, 'assets/gpg-keyrings-PC1/wheezy')


class CheckRequestedDebianRelease(Task):
    description = 'Checking whether there is a release available for {info.manifest.release}'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        if info.manifest.release not in (jessie, wheezy, stretch):
            msg = 'Debian {info.manifest.release} is not (yet) available in the Puppetlabs.com APT repository.'
            raise TaskError(msg)


class CheckAssetsPath(Task):
    description = 'Checking whether the assets path exist'
    phase = phases.validation
    predecessors = [CheckRequestedDebianRelease]

    @classmethod
    def run(cls, info):
        assets = info.manifest.plugins['puppet']['assets']
        if not os.path.exists(assets):
            msg = 'The assets directory {assets} does not exist.'.format(assets=assets)
            raise TaskError(msg)
        if not os.path.isdir(assets):
            msg = 'The assets path {assets} does not point to a directory.'.format(assets=assets)
            raise TaskError(msg)


class CheckManifestPath(Task):
    description = 'Checking whether the manifest file path exist inside the assets'
    phase = phases.validation
    predecessors = [CheckAssetsPath]

    @classmethod
    def run(cls, info):
        manifest = info.manifest.plugins['puppet']['manifest']
        if not os.path.exists(manifest):
            msg = 'The manifest file {manifest} does not exist.'.format(manifest=manifest)
            raise TaskError(msg)
        if not os.path.isfile(manifest):
            msg = 'The manifest path {manifest} does not point to a file.'.format(manifest=manifest)
            raise TaskError(msg)


class InstallPuppetlabsPC1ReleaseKey(Task):
    description = 'Install puppetlabs PC1 Release key into the keyring'
    phase = phases.package_installation
    successors = [apt.WriteSources]

    @classmethod
    def run(cls, info):
        from shutil import copy
        if (info.manifest.release == stretch):
            key_path = os.path.join(ASSETS_DIR_STRETCH, 'puppetlabs-pc1-keyring.gpg')
        if (info.manifest.release == jessie):
            key_path = os.path.join(ASSETS_DIR_JESSIE, 'puppetlabs-pc1-keyring.gpg')
        if (info.manifest.release == wheezy):
            key_path = os.path.join(ASSETS_DIR_WHEEZY, 'puppetlabs-pc1-keyring.gpg')
        destination = os.path.join(info.root, 'etc/apt/trusted.gpg.d/puppetlabs-pc1-keyring.gpg')
        copy(key_path, destination)


class AddPuppetlabsPC1SourcesList(Task):
    description = 'Adding Puppetlabs APT repo to the list of sources.'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        if (info.manifest.release == stretch):
            info.source_lists.add('puppetlabs', 'deb http://apt.puppetlabs.com stretch PC1')
        if (info.manifest.release == jessie):
            info.source_lists.add('puppetlabs', 'deb http://apt.puppetlabs.com jessie PC1')
        if (info.manifest.release == wheezy):
            info.source_lists.add('puppetlabs', 'deb http://apt.puppetlabs.com wheezy PC1')


class InstallPuppetAgent(Task):
    description = 'Install puppet-agent from https://apt.puppetlabs.com for {system.release}'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        log_check_call(['chroot', info.root, 'apt-get', 'install', '--assume-yes', 'puppet-agent'])


class InstallModules(Task):
    description = 'Installing Puppet modules'
    phase = phases.system_modification
    predecessors = [InstallPuppetAgent]

    @classmethod
    def run(cls, info):
        for module in info.manifest.plugins['puppet']['install_modules']:
            command = ['chroot', info.root, '/opt/puppetlabs/bin/puppet', 'module', 'install', '--force']
            if (len(module) == 1):
                [module_name] = module
                command.append(str(module_name))
            if (len(module) == 2):
                [module_name, module_version] = module
                command.append(str(module_name))
                command.append('--version')
                command.append(str(module_version))
            log_check_call(command)


class CopyPuppetAssets(Task):
    description = 'Copying declared custom puppet assets.'
    phase = phases.system_modification
    predecessors = [InstallModules]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import copy_tree
        copy_tree(info.manifest.plugins['puppet']['assets'], os.path.join(info.root, 'etc/puppetlabs/'))


class ApplyPuppetManifest(Task):
    description = 'Applying puppet manifest.'
    phase = phases.system_modification
    predecessors = [CopyPuppetAssets]

    @classmethod
    def run(cls, info):
        with open(os.path.join(info.root, 'etc/hostname')) as handle:
            hostname = handle.read().strip()
        with open(os.path.join(info.root, 'etc/hosts'), 'a') as handle:
            handle.write('127.0.0.1\t{hostname}\n'.format(hostname=hostname))
        from shutil import copy
        pp_manifest = info.manifest.plugins['puppet']['manifest']
        manifest_rel_dst = os.path.join('tmp', os.path.basename(pp_manifest))
        manifest_dst = os.path.join(info.root, manifest_rel_dst)
        copy(pp_manifest, manifest_dst)
        manifest_path = os.path.join('/', manifest_rel_dst)
        log_check_call(['chroot', info.root, 'puppet', 'apply', '--verbose', '--debug', manifest_path])
        os.remove(manifest_dst)
        hosts_path = os.path.join(info.root, 'etc/hosts')
        sed_i(hosts_path, r'127.0.0.1\s*{hostname}\n?'.format(hostname=hostname), '')


class EnableAgent(Task):
    description = 'Enabling the puppet agent'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        puppet_defaults = os.path.join(info.root, 'etc/defaults/puppet')
        sed_i(puppet_defaults, 'START=no', 'START=yes')
