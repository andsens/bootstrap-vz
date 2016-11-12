from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.exceptions import TaskError
from bootstrapvz.common.tools import log_check_call, rel_path
from ebs import Snapshot
from bootstrapvz.common.tasks import workspace
import connection
from . import assets
import os.path

cert_ec2 = os.path.join(assets, 'certs/cert-ec2.pem')


class AMIName(Task):
    description = 'Determining the AMI name'
    phase = phases.preparation
    predecessors = [connection.SilenceBotoDebug, connection.Connect]

    @classmethod
    def run(cls, info):
        ami_name = info.manifest.name.format(**info.manifest_vars)
        ami_description = info.manifest.provider['description'].format(**info.manifest_vars)

        images = info._ec2['connection'].describe_images(Owners=['self'])['Images']
        for image in images:
            if ami_name == image['Name']:
                msg = 'An image by the name {ami_name} already exists.'.format(ami_name=ami_name)
                raise TaskError(msg)
        info._ec2['ami_name'] = ami_name
        info._ec2['ami_description'] = ami_description


class BundleImage(Task):
    description = 'Bundling the image'
    phase = phases.image_registration

    @classmethod
    def run(cls, info):
        bundle_name = 'bundle-' + info.run_id
        info._ec2['bundle_path'] = os.path.join(info.workspace, bundle_name)
        arch = {'i386': 'i386', 'amd64': 'x86_64'}.get(info.manifest.system['architecture'])
        log_check_call(['euca-bundle-image',
                        '--image', info.volume.image_path,
                        '--arch', arch,
                        '--user', info.credentials['user-id'],
                        '--privatekey', info.credentials['private-key'],
                        '--cert', info.credentials['certificate'],
                        '--ec2cert', cert_ec2,
                        '--destination', info._ec2['bundle_path'],
                        '--prefix', info._ec2['ami_name']])


class UploadImage(Task):
    description = 'Uploading the image bundle'
    phase = phases.image_registration
    predecessors = [BundleImage]

    @classmethod
    def run(cls, info):
        manifest_file = os.path.join(info._ec2['bundle_path'], info._ec2['ami_name'] + '.manifest.xml')
        if info._ec2['region'] == 'us-east-1':
            s3_url = 'https://s3.amazonaws.com/'
        elif info._ec2['region'] == 'cn-north-1':
            s3_url = 'https://s3.cn-north-1.amazonaws.com.cn'
        else:
            s3_url = 'https://s3-{region}.amazonaws.com/'.format(region=info._ec2['region'])
        info._ec2['manifest_location'] = info.manifest.provider['bucket'] + '/' + info._ec2['ami_name'] + '.manifest.xml'
        log_check_call(['euca-upload-bundle',
                        '--bucket', info.manifest.provider['bucket'],
                        '--manifest', manifest_file,
                        '--access-key', info.credentials['access-key'],
                        '--secret-key', info.credentials['secret-key'],
                        '--url', s3_url,
                        '--region', info._ec2['region']])


class RemoveBundle(Task):
    description = 'Removing the bundle files'
    phase = phases.cleaning
    successors = [workspace.DeleteWorkspace]

    @classmethod
    def run(cls, info):
        from shutil import rmtree
        rmtree(info._ec2['bundle_path'])
        del info._ec2['bundle_path']


class RegisterAMI(Task):
    description = 'Registering the image as an AMI'
    phase = phases.image_registration
    predecessors = [Snapshot, UploadImage]

    @classmethod
    def run(cls, info):
        registration_params = {'Name': info._ec2['ami_name'],
                               'Description': info._ec2['ami_description']}
        registration_params['Architecture'] = {'i386': 'i386',
                                               'amd64': 'x86_64'}.get(info.manifest.system['architecture'])

        if info.manifest.volume['backing'] == 's3':
            registration_params['ImageLocation'] = info._ec2['manifest_location']
        else:
            root_dev_name = {'pvm': '/dev/sda',
                             'hvm': '/dev/xvda'}.get(info.manifest.provider['virtualization'])
            registration_params['RootDeviceName'] = root_dev_name

            block_device = [{'DeviceName': root_dev_name,
                             'Ebs': {
                                 'SnapshotId': info._ec2['snapshot'],
                                 'VolumeSize': info.volume.size.bytes.get_qty_in('GiB'),
                                 'VolumeType': 'gp2',
                                 'DeleteOnTermination': True}}]
            registration_params['BlockDeviceMappings'] = block_device

        if info.manifest.provider['virtualization'] == 'hvm':
            registration_params['VirtualizationType'] = 'hvm'
        else:
            registration_params['VirtualizationType'] = 'paravirtual'
            akis_path = rel_path(__file__, 'ami-akis.yml')
            from bootstrapvz.common.tools import config_get
            registration_params['kernel_id'] = config_get(akis_path,
                                                          [info._ec2['region'],
                                                           info.manifest.system['architecture']])

        if info.manifest.provider.get('enhanced_networking', None) == 'simple':
            registration_params['SriovNetSupport'] = 'simple'
            registration_params['EnaSupport'] = True

        info._ec2['image'] = info._ec2['connection'].register_image(**registration_params)

        # Setting up tags on the AMI
        if 'tags' in info.manifest.data:
            raw_tags = info.manifest.data['tags']
            formatted_tags = {k: v.format(**info.manifest_vars) for k, v in raw_tags.items()}
            tags = [{'Key': k, 'Value': v} for k, v in formatted_tags.items()]
            info._ec2['connection'].create_tags(Resources=[info._ec2['image']['ImageId']],
                                                Tags=tags)
