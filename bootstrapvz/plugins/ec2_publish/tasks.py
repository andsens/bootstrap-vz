from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.ec2.tasks import ami

import logging


class CopyAmiToRegions(Task):
    description = 'Copy AWS AMI over other regions'
    phase = phases.image_registration
    predecessors = [ami.RegisterAMI]

    @classmethod
    def run(cls, info):
        source_region = info._ec2['region']
        source_ami = info._ec2['image']
        name = info._ec2['ami_name']
        copy_description = "Copied from %s (%s)" % (source_ami, source_region)

        connect_args = {
            'aws_access_key_id': info.credentials['access-key'],
            'aws_secret_access_key': info.credentials['secret-key']
        }
        if 'security-token' in info.credentials:
            connect_args['security_token'] = info.credentials['security-token']

        region_amis = {source_region: source_ami}
        region_conns = {source_region: info._ec2['connection']}
        from boto.ec2 import connect_to_region
        regions = info.manifest.plugins['ec2_publish'].get('regions', ())
        for region in regions:
            conn = connect_to_region(region, **connect_args)
            region_conns[region] = conn
            copied_image = conn.copy_image(source_region, source_ami, name=name, description=copy_description)
            region_amis[region] = copied_image.image_id
        info._ec2['region_amis'] = region_amis
        info._ec2['region_conns'] = region_conns


class PublishAmiManifest(Task):
    description = 'Publish a manifest of generated AMIs'
    phase = phases.image_registration
    predecessors = [CopyAmiToRegions]

    @classmethod
    def run(cls, info):
        manifest_url = info.manifest.plugins['ec2_publish']['manifest_url']

        import json
        amis_json = json.dumps(info._ec2['region_amis'])

        from urlparse import urlparse
        parsed_url = urlparse(manifest_url)
        parsed_host = parsed_url.netloc
        if not parsed_url.scheme:
            with open(parsed_url.path, 'w') as local_out:
                local_out.write(amis_json)
        elif parsed_host.endswith('amazonaws.com') and 's3' in parsed_host:
            region = 'us-east-1'
            path = parsed_url.path[1:]
            if 's3-' in parsed_host:
                loc = parsed_host.find('s3-') + 3
                region = parsed_host[loc:parsed_host.find('.', loc)]

            if '.s3' in parsed_host:
                bucket = parsed_host[:parsed_host.find('.s3')]
            else:
                bucket, path = path.split('/', 1)

            from boto.s3 import connect_to_region
            conn = connect_to_region(region)
            key = conn.get_bucket(bucket, validate=False).new_key(path)
            headers = {'Content-Type': 'application/json'}
            key.set_contents_from_string(amis_json, headers=headers, policy='public-read')


class PublishAmi(Task):
    description = 'Make generated AMIs public'
    phase = phases.image_registration
    predecessors = [CopyAmiToRegions]

    @classmethod
    def run(cls, info):
        region_conns = info._ec2['region_conns']
        region_amis = info._ec2['region_amis']
        logger = logging.getLogger(__name__)

        import time
        for region, region_ami in region_amis.items():
            conn = region_conns[region]
            current_image = conn.get_image(region_ami)
            while current_image.state == 'pending':
                logger.debug('Waiting for %s in %s (currently: %s)', region_ami, region, current_image.state)
                time.sleep(5)
                current_image = conn.get_image(region_ami)
            conn.modify_image_attribute(region_ami, attribute='launchPermission', operation='add', groups='all')
