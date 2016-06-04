from bootstrapvz.base import Task
from .. import phases
import os.path


class LocaleBootstrapPackage(Task):
    description = 'Adding locale package to bootstrap installation'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        # We could bootstrap without locales, but things just suck without them
        # eg. error messages when running apt
        info.include_packages.add('locales')


class GenerateLocale(Task):
    description = 'Generating system locale'
    phase = phases.package_installation

    @classmethod
    def run(cls, info):
        from ..tools import sed_i
        from ..tools import log_check_call

        lang = '{locale}.{charmap}'.format(locale=info.manifest.system['locale'],
                                           charmap=info.manifest.system['charmap'])
        locale_str = '{locale}.{charmap} {charmap}'.format(locale=info.manifest.system['locale'],
                                                           charmap=info.manifest.system['charmap'])

        search = '# ' + locale_str
        locale_gen = os.path.join(info.root, 'etc/locale.gen')
        sed_i(locale_gen, search, locale_str)

        log_check_call(['chroot', info.root, 'locale-gen'])
        log_check_call(['chroot', info.root,
                        'update-locale', 'LANG=' + lang])


class SetTimezone(Task):
    description = 'Setting the selected timezone'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        tz_path = os.path.join(info.root, 'etc/timezone')
        timezone = info.manifest.system['timezone']
        with open(tz_path, 'w') as tz_file:
            tz_file.write(timezone)


class SetLocalTimeLink(Task):
    description = 'Setting the selected local timezone (link)'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        timezone = info.manifest.system['timezone']
        localtime_path = os.path.join(info.root, 'etc/localtime')
        os.unlink(localtime_path)
        os.symlink(os.path.join('/usr/share/zoneinfo', timezone), localtime_path)


class SetLocalTimeCopy(Task):
    description = 'Setting the selected local timezone (copy)'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from shutil import copy
        timezone = info.manifest.system['timezone']
        zoneinfo_path = os.path.join(info.root, '/usr/share/zoneinfo', timezone)
        localtime_path = os.path.join(info.root, 'etc/localtime')
        copy(zoneinfo_path, localtime_path)
