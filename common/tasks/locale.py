from base import Task
from common import phases
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
	description = 'Generating the selected locale'
	phase = phases.package_installation

	@classmethod
	def run(cls, info):
		from common.tools import sed_i
		from common.tools import log_check_call
		locale_gen = os.path.join(info.root, 'etc/locale.gen')
		locale_str = '{locale}.{charmap} {charmap}'.format(locale=info.manifest.system['locale'],
		                                                   charmap=info.manifest.system['charmap'])
		search = '# ' + locale_str
		sed_i(locale_gen, search, locale_str)

		log_check_call(['chroot', info.root, 'locale-gen'])

		lang = '{locale}.{charmap}'.format(locale=info.manifest.system['locale'],
		                                   charmap=info.manifest.system['charmap'])
		log_check_call(['chroot', info.root,
		                'update-locale', 'LANG=' + lang])


class SetTimezone(Task):
	description = 'Setting the selected timezone'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from shutil import copy
		tz_path = os.path.join(info.root, 'etc/timezone')
		timezone = info.manifest.system['timezone']
		with open(tz_path, 'w') as tz_file:
			tz_file.write(timezone)
		zoneinfo_path = os.path.join(info.root, '/usr/share/zoneinfo', timezone)
		localtime_path = os.path.join(info.root, 'etc/localtime')
		copy(zoneinfo_path, localtime_path)
