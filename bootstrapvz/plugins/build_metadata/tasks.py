from base import Task
from common import phases


class WriteMetadata(Task):
	description = 'Writing bootstrap metadata to file'
	phase = phases.cleaning

	@classmethod
	def run(cls, info):
		metadata_path = info.manifest.plugins['build_metadata']['path']
		with open(metadata_path, 'w') as metadata:
			metadata.write(('AMI_ID={ami_id}\n'
			                'AMI_NAME={ami_name}'
			                'SNAPSHOT_ID={snapshot_id}'
			                .format(ami_id=info.image,
			                        ami_name=info.ami_name,
			                        snapshot_id=info.snapshot.id)))
