from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import host


class AddExternalCommands(Task):
    description = 'Determining required external commands for EC2 bootstrapping'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        if info.manifest.volume['backing'] == 's3':
            info.host_dependencies['euca-bundle-image'] = 'euca2ools'
            info.host_dependencies['euca-upload-bundle'] = 'euca2ools'


class GetInstanceMetadata(Task):
    description = 'Retrieving instance metadata'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        import urllib2
        import json
        metadata_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
        response = urllib2.urlopen(url=metadata_url, timeout=5)
        info._ec2['host'] = json.load(response)
        info._ec2['region'] = info._ec2['host']['region']


class SetRegion(Task):
    description = 'Setting the AWS region'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info._ec2['region'] = info.manifest.provider['region']
