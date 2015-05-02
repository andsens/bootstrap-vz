from bootstrapvz.base import Task
from bootstrapvz.common import phases
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
		if 'credentials' in manifest.provider:
			if all(key in manifest.provider['credentials'] for key in keys):
				for key in keys:
					creds[key] = manifest.provider['credentials'][key]
				return creds

		def env_key(key):
			return ('aws-' + key).upper().replace('-', '_')
		if all(getenv(env_key(key)) is not None for key in keys):
			for key in keys:
				creds[key] = getenv(env_key(key))
			return creds

		def provider_key(key):
			return key.replace('-', '_')
		import boto.provider
		provider = boto.provider.Provider('aws')
		if all(getattr(provider, provider_key(key)) is not None for key in keys):
			for key in keys:
				creds[key] = getattr(provider, provider_key(key))
			return creds
		raise RuntimeError(('No ec2 credentials found, they must all be specified '
		                    'exclusively via environment variables or through the manifest.'))


class Connect(Task):
	description = 'Connecting to EC2'
	phase = phases.preparation
	predecessors = [GetCredentials, host.GetInstanceMetadata, host.SetRegion]

	@classmethod
	def run(cls, info):
		from boto.ec2 import connect_to_region
		info._ec2['connection'] = connect_to_region(info._ec2['region'],
		                                            aws_access_key_id=info.credentials['access-key'],
		                                            aws_secret_access_key=info.credentials['secret-key'])
