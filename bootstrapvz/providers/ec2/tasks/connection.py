from base import Task
from common import phases
import host


class GetCredentials(Task):
	description = 'Getting AWS credentials'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		keys = ['access-key', 'secret-key']
		if info.manifest.volume['backing'] == 's3':
			keys.extend(['certificate', 'private-key', 'user-id'])
		info.credentials = cls.get_credentials(info.manifest, keys)

	@classmethod
	def get_credentials(cls, manifest, keys):
		from os import getenv
		creds = {}
		if all(key in manifest.data['credentials'] for key in keys):
			for key in keys:
				creds[key] = manifest.data['credentials'][key]
			return creds

		def env_key(key):
			return ('aws-' + key).upper().replace('-', '_')
		if all(getenv(env_key(key)) is not None for key in keys):
			for key in keys:
				creds[key] = getenv(env_key(key))
			return creds
		raise RuntimeError(('No ec2 credentials found, they must all be specified '
		                    'exclusively via environment variables or through the manifest.'))


class Connect(Task):
	description = 'Connecting to EC2'
	phase = phases.preparation
	predecessors = [GetCredentials, host.GetInfo]

	@classmethod
	def run(cls, info):
		from boto.ec2 import connect_to_region
		info.connection = connect_to_region(info.host['region'],
		                                    aws_access_key_id=info.credentials['access-key'],
		                                    aws_secret_access_key=info.credentials['secret-key'])
