from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import bootstrap, dpkg, workspace
from bootstrapvz.common.tools import sed_i
import os
import shutil
from . import assets


class InitializeBootstrapFilterList(Task):
    description = 'Initializing the bootstrapping filter list'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info._minimize_size['bootstrap_filter'] = {'exclude': [], 'include': []}


class CreateBootstrapFilterScripts(Task):
    description = 'Creating the bootstrapping locales filter script'
    phase = phases.os_installation
    successors = [bootstrap.Bootstrap]
    # Inspired by:
    # https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap

    @classmethod
    def run(cls, info):
        if info.bootstrap_script is not None:
            from bootstrapvz.common.exceptions import TaskError
            raise TaskError('info.bootstrap_script seems to already be set '
                            'and is conflicting with this task')

        bootstrap_script = os.path.join(info.workspace, 'bootstrap_script.sh')
        filter_script = os.path.join(info.workspace, 'bootstrap_files_filter.sh')
        excludes_file = os.path.join(info.workspace, 'debootstrap-excludes')

        shutil.copy(os.path.join(assets, 'bootstrap-script.sh'), bootstrap_script)
        shutil.copy(os.path.join(assets, 'bootstrap-files-filter.sh'), filter_script)

        sed_i(bootstrap_script, r'DEBOOTSTRAP_EXCLUDES_PATH', excludes_file)
        sed_i(bootstrap_script, r'BOOTSTRAP_FILES_FILTER_PATH', filter_script)

        # We exclude with patterns but include with fixed strings
        # The pattern matching when excluding is needed in order to filter
        # everything below e.g. /usr/share/locale but not the folder itself
        filter_lists = info._minimize_size['bootstrap_filter']
        exclude_list = r'\|'.join(map(lambda p: '.' + p + r'.\+', filter_lists['exclude']))
        include_list = '\n'.join(map(lambda p: '.' + p, filter_lists['include']))
        sed_i(filter_script, r'EXCLUDE_PATTERN', exclude_list)
        sed_i(filter_script, r'INCLUDE_PATHS', include_list)
        os.chmod(filter_script, 0o755)

        info.bootstrap_script = bootstrap_script
        info._minimize_size['filter_script'] = filter_script


class FilterLocales(Task):
    description = 'Configuring dpkg and debootstrap to only include specific locales/manpages when installing packages'
    phase = phases.os_installation
    predecessors = [dpkg.CreateDpkgCfg]
    successors = [CreateBootstrapFilterScripts]
    # Snatched from:
    # https://github.com/docker/docker/blob/1d775a54cc67e27f755c7338c3ee938498e845d7/contrib/mkimage/debootstrap
    # and
    # https://raphaelhertzog.com/2010/11/15/save-disk-space-by-excluding-useless-files-with-dpkg/

    @classmethod
    def run(cls, info):
        # Filter when debootstrapping
        info._minimize_size['bootstrap_filter']['exclude'].extend([
            '/usr/share/locale/',
            '/usr/share/man/',
        ])

        locales = info.manifest.plugins['minimize_size']['dpkg']['locales']
        info._minimize_size['bootstrap_filter']['include'].extend([
            '/usr/share/locale/locale.alias',
            '/usr/share/man/man1',
            '/usr/share/man/man2',
            '/usr/share/man/man3',
            '/usr/share/man/man4',
            '/usr/share/man/man5',
            '/usr/share/man/man6',
            '/usr/share/man/man7',
            '/usr/share/man/man8',
            '/usr/share/man/man9',
        ] +
            map(lambda l: '/usr/share/locale/' + l + '/', locales) +
            map(lambda l: '/usr/share/man/' + l + '/', locales)
        )

        # Filter when installing things with dpkg
        locale_lines = ['path-exclude=/usr/share/locale/*',
                        'path-include=/usr/share/locale/locale.alias']
        manpages_lines = ['path-exclude=/usr/share/man/*',
                          'path-include=/usr/share/man/man[1-9]']

        locales = info.manifest.plugins['minimize_size']['dpkg']['locales']
        locale_lines.extend(map(lambda l: 'path-include=/usr/share/locale/' + l + '/*', locales))
        manpages_lines.extend(map(lambda l: 'path-include=/usr/share/man/' + l + '/*', locales))

        locales_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d/10filter-locales')
        manpages_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d/10filter-manpages')

        with open(locales_path, 'w') as locale_filter:
            locale_filter.write('\n'.join(locale_lines) + '\n')
        with open(manpages_path, 'w') as manpages_filter:
            manpages_filter.write('\n'.join(manpages_lines) + '\n')


class ExcludeDocs(Task):
    description = 'Configuring dpkg and debootstrap to not install additional documentation for packages'
    phase = phases.os_installation
    predecessors = [dpkg.CreateDpkgCfg]
    successors = [CreateBootstrapFilterScripts]

    @classmethod
    def run(cls, info):
        # "Packages must not require the existence of any files in /usr/share/doc/ in order to function [...]."
        # Source: https://www.debian.org/doc/debian-policy/ch-docs.html
        # So doing this should cause no problems.
        info._minimize_size['bootstrap_filter']['exclude'].append('/usr/share/doc/')
        exclude_docs_path = os.path.join(info.root, 'etc/dpkg/dpkg.cfg.d/10exclude-docs')
        with open(exclude_docs_path, 'w') as exclude_docs:
            exclude_docs.write('path-exclude=/usr/share/doc/*\n')


class DeleteBootstrapFilterScripts(Task):
    description = 'Deleting the bootstrapping locales filter script'
    phase = phases.cleaning
    successors = [workspace.DeleteWorkspace]

    @classmethod
    def run(cls, info):
        os.remove(info._minimize_size['filter_script'])
        del info._minimize_size['filter_script']
        os.remove(info.bootstrap_script)
