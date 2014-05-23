from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
import os
import urllib2


class CheckAptProxy(Task):
	description = 'Checking reachability of APT proxy server'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		proxy_address = info.manifest.plugins['apt_proxy']['address']
		proxy_port = info.manifest.plugins['apt_proxy']['port']
		proxy_url = 'http://{address}:{port}'.format(address=proxy_address, port=proxy_port)
		try:
			urllib2.urlopen(proxy_url, timeout=5)
		except Exception as e:
			# Default response from `apt-cacher-ng`
			if isinstance(e, urllib2.HTTPError) and e.code == 404 and e.msg == 'Usage Information':
				pass
			else:
				import logging
				log = logging.getLogger(__name__)
				log.warning('The APT proxy server couldn\'t be reached. `apt-get\' commands may fail.')


class SetAptProxy(Task):
	description = 'Setting proxy for APT'
	phase = phases.package_installation
	successors = [apt.AptUpdate]

	@classmethod
	def run(cls, info):
		proxy_path = os.path.join(info.root, 'etc/apt/apt.conf.d/02proxy')
		proxy_address = info.manifest.plugins['apt_proxy']['address']
		proxy_port = info.manifest.plugins['apt_proxy']['port']
		with open(proxy_path, 'w') as proxy_file:
			proxy_file.write('Acquire::http {{ Proxy "http://{address}:{port}"; }};\n'
			                 .format(address=proxy_address, port=proxy_port))


class RemoveAptProxy(Task):
	description = 'Removing APT proxy configuration file'
	phase = phases.system_cleaning

	@classmethod
	def run(cls, info):
		os.remove(os.path.join(info.root, 'etc/apt/apt.conf.d/02proxy'))
