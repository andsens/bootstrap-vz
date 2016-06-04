from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.oracle.apiclient import OracleStorageAPIClient


class Connect(Task):
    description = 'Connecting to the Oracle Storage Cloud API'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info._oracle['client'] = OracleStorageAPIClient(
            username=info.manifest.provider['credentials']['username'],
            password=info.manifest.provider['credentials']['password'],
            identity_domain=info.manifest.provider['credentials']['identity-domain'],
            container=info.manifest.provider['container'],
        )
        # Try to fetch the token, so it will fail early if the credentials are wrong
        info._oracle['client'].auth_token
