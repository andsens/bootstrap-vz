from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
import os


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
