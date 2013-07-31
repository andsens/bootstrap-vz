from base import Task
from common import phases
import os.path


class GenerateLocale(Task):
	description = 'Generating the selected locale'
	phase = phases.system_modification

	def run(self, info):
		from common.tools import sed_i
		from common.tools import log_check_call
		locale_gen = os.path.join(info.root, 'etc/locale.gen')
		locale_str = '{locale}.{charmap} {charmap}'.format(locale=info.manifest.system['locale'],
		                                                   charmap=info.manifest.system['charmap'])
		search = '# ' + locale_str
		sed_i(locale_gen, search, locale_str)

		command = ['/usr/sbin/chroot', info.root, '/usr/sbin/locale-gen']
		log_check_call(command)


class SetTimezone(Task):
	description = 'Setting the selected timezone'
	phase = phases.system_modification

	def run(self, info):
		from shutil import copy
		tz_path = os.path.join(info.root, 'etc/timezone')
		timezone = info.manifest.system['timezone']
		with open(tz_path, 'w') as tz_file:
			tz_file.write(timezone)
		zoneinfo_path = os.path.join(info.root, '/usr/share/zoneinfo', timezone)
		localtime_path = os.path.join(info.root, 'etc/localtime')
		copy(zoneinfo_path, localtime_path)
