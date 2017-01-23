from bootstrapvz.base import Task
from bootstrapvz.common import phases
import host


class SilenceBotoDebug(Task):
    description = 'Silence boto debug logging'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        # Regardless of of loglevel, we don't want boto debug stuff, it's very noisy
        import logging
        logging.getLogger('boto').setLevel(logging.INFO)


class GetCredentials(Task):
    description = 'Getting AWS credentials'
    phase = phases.preparation
    successors = [SilenceBotoDebug]

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
            if hasattr(provider, 'security_token'):
                creds['security-token'] = provider.security_token
            return creds
        raise RuntimeError(('No ec2 credentials found, they must all be specified '
                            'exclusively via environment variables or through the manifest.'))


class Connect(Task):
    description = 'Connecting to EC2'
    phase = phases.preparation
    predecessors = [GetCredentials, host.GetInstanceMetadata, host.SetRegion]

    @classmethod
    def run(cls, info):
        import boto3
        connect_args = {
            'aws_access_key_id': info.credentials['access-key'],
            'aws_secret_access_key': info.credentials['secret-key']
        }

        if 'security-token' in info.credentials:
            connect_args['security_token'] = info.credentials['security-token']

        info._ec2['connection'] = boto3.Session(info._ec2['region'],
                                                info.credentials['access-key'],
                                                info.credentials['secret-key'])
        info._ec2['connection'] = boto3.client('ec2', region_name=info._ec2['region'])
