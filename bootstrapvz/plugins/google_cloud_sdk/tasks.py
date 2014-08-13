from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import workspace
from bootstrapvz.common.tools import log_check_call
import os


class InstallCloudSDK(Task):
	description = 'Install Cloud SDK, not yet packaged'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		import contextlib
		import re
		import urllib
		import urlparse

		# The current download URL needs to be determined dynamically via a sha1sum file. Here's the
		# necessary logic.

		cloudsdk_download_site = 'https://dl.google.com/dl/cloudsdk/release/'
		cloudsdk_filelist_url = urlparse.urljoin(cloudsdk_download_site, 'sha1.txt')
		cloudsdk_pathname_regexp = r'^packages/google-cloud-sdk-coretools-linux-[0-9]+\.tar\.gz$'
		cloudsdk_filename = ''  # This is set in the 'with' block below.

		with contextlib.closing(urllib.urlopen(cloudsdk_filelist_url)) as cloudsdk_filelist:
			# cloudsdk_filelist is in sha1sum format, so <hash><whitespace><pathname>
			# pathname is a suffix relative to cloudsdk_download_site
			#
			# Retrieve the pathname which matches cloudsdk_pathname_regexp. It's currently safe to
			# assume that only one pathname will match.
			for cloudsdk_filelist_line in cloudsdk_filelist:
				_, pathname = cloudsdk_filelist_line.split()
				if re.match(cloudsdk_pathname_regexp, pathname):
					# Don't use os.path.basename since we're actually parsing a URL
					# suffix, not a path. Same probable result, but wrong semantics.
					#
					# The format of pathname is already known to match
					# cloudsdk_pathname_regexp, so this is safe.
					_, cloudsdk_filename = pathname.rsplit('/', 1)
					break

		cloudsdk_download_dest = os.path.join(info.workspace, cloudsdk_filename)

		cloudsdk_url = urlparse.urljoin(cloudsdk_download_site, pathname)

		urllib.urlretrieve(cloudsdk_url, cloudsdk_download_dest)

		# Make a "mental note" of which file to remove in the system cleaning phase.
		info._google_cloud_sdk['tarball_pathname'] = cloudsdk_download_dest

		cloudsdk_directory = os.path.join(info.root, 'usr/local/share/google')
		os.makedirs(cloudsdk_directory)
		log_check_call(['tar', 'xaf', cloudsdk_download_dest, '-C', cloudsdk_directory])

		# We need to symlink certain programs from the Cloud SDK bin directory into /usr/local/bin.
		# Keep a list and do it in a unified way. Naturally this will go away with proper packaging.
		gcloud_programs = ['bq', 'gsutil', 'gcutil', 'gcloud', 'git-credential-gcloud.sh']
		for prog in gcloud_programs:
			src = os.path.join('..', 'share', 'google', 'google-cloud-sdk', 'bin', prog)
			dest = os.path.join(info.root, 'usr', 'local', 'bin', prog)
			os.symlink(src, dest)


class RemoveCloudSDKTarball(Task):
	description = 'Remove tarball for Cloud SDK'
	phase = phases.system_cleaning
	successors = [workspace.DeleteWorkspace]

	@classmethod
	def run(cls, info):
		os.remove(info._google_cloud_sdk['tarball_pathname'])
