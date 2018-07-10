from bootstrapvz.base import Task
from bootstrapvz.common import phases
from . import host


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

        provider_args = {
            'profile_name': manifest.provider.get('profile', None)}

        from boto3 import Session
        if provider_args.get('profile_name', None):
            if provider_args.get('profile_name') not in Session().available_profiles:
                raise RuntimeError((
                    'Profile specified was not found: {}'.format(provider_args.get('profile_name'))))
        provider = Session(**provider_args).get_credentials()
        if provider is not None:
            provider = provider.get_frozen_credentials()
        if all(getattr(provider, provider_key(key), None) is not None for key in keys):
            for key in keys:
                creds[key] = getattr(provider, provider_key(key))
            if hasattr(provider, 'token'):
                creds['security-token'] = provider.token
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

        connect_args['aws_session_token'] = info.credentials.get('security-token', None)

        info._ec2['connection'] = boto3.client('ec2', region_name=info._ec2['region'], **connect_args)
