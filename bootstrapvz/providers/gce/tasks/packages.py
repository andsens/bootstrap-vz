from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tools import log_check_call
import os


class DefaultPackages(Task):
	description = 'Adding image packages required for GCE'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('python')
		info.packages.add('sudo')
		info.packages.add('ntp')
		info.packages.add('lsb-release')
		info.packages.add('acpi-support-base')
		info.packages.add('openssh-client')
		info.packages.add('openssh-server')
		info.packages.add('dhcpd')

		kernel_packages_path = os.path.join(os.path.dirname(__file__), '../../ec2/tasks/packages-kernels.json')
		from bootstrapvz.common.tools import config_get
		kernel_package = config_get(kernel_packages_path, [info.release_codename,
		                                                   info.manifest.system['architecture']])
		info.packages.add(kernel_package)


class GooglePackages(Task):
	description = 'Adding image packages required for GCE from Google repositories'
	phase = phases.preparation
	predecessors = [DefaultPackages]

	@classmethod
	def run(cls, info):
		info.packages.add('google-compute-daemon')
		info.packages.add('google-startup-scripts')
		info.packages.add('python-gcimagebundle')
		info.packages.add('gcutil')


class InstallGSUtil(Task):
	description = 'Install gsutil, not yet packaged'
	phase = phases.package_installation

	@classmethod
	def run(cls, info):
		gsutil_tarball = os.path.join(info.manifest.bootstrapper['workspace'], 'gsutil.tar.gz')
		log_check_call(['wget', '--output-document', gsutil_tarball,
		                'http://storage.googleapis.com/pub/gsutil.tar.gz'])
		gsutil_directory = os.path.join(info.root, 'usr/local/share/google')
		gsutil_binary = os.path.join(os.path.join(info.root, 'usr/local/bin'), 'gsutil')
		os.makedirs(gsutil_directory)
		log_check_call(['tar', 'xaf', gsutil_tarball, '-C', gsutil_directory])
		os.remove(gsutil_tarball)
		log_check_call(['ln', '-s', '../share/google/gsutil/gsutil', gsutil_binary])
