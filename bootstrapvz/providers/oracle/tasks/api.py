from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.oracle.apiclient import OracleStorageAPIClient


class InstantiateAPIClient(Task):
	description = 'Instantiating Oracle Storage Cloud API client'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		info._oracle['client'] = OracleStorageAPIClient(
		    username=info.manifest.provider['credentials']['username'],
		    password=info.manifest.provider['credentials']['password'],
		    identity_domain=info.manifest.provider['credentials']['identity-domain'],
		    container=info.manifest.provider['container'],
		)
