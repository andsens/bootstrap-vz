from bootstrapvz.base import Task
from bootstrapvz.common import phases


class Create(Task):
    description = 'Creating the EBS volume'
    phase = phases.volume_creation

    @classmethod
    def run(cls, info):
        info.volume.create(info._ec2['connection'], info._ec2['host']['availabilityZone'])


class Attach(Task):
    description = 'Attaching the volume'
    phase = phases.volume_creation
    predecessors = [Create]

    @classmethod
    def run(cls, info):
        info.volume.attach(info._ec2['host']['instanceId'])


class Snapshot(Task):
    description = 'Creating a snapshot of the EBS volume'
    phase = phases.image_registration

    @classmethod
    def run(cls, info):
        info._ec2['snapshot'] = info.volume.snapshot()

        # Setting up tags on the snapshot
        if 'tags' in info.manifest.data:
            raw_tags = info.manifest.data['tags']
            formatted_tags = {k: v.format(**info.manifest_vars) for k, v in raw_tags.items()}
            tags = [{'Key': k, 'Value': v} for k, v in formatted_tags.items()]
            info._ec2['connection'].create_tags(Resources=[info._ec2['snapshot']],
                                                Tags=tags)
