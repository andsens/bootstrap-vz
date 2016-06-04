

class BuildServer(object):

    def __init__(self, name, settings):
        self.name = name
        self.settings = settings
        self.build_settings = settings.get('build_settings', {})
        self.run_settings = settings.get('run_settings', {})
        self.can_bootstrap = settings['can_bootstrap']
        self.release = settings.get('release', None)

    def apply_build_settings(self, manifest_data):
        if manifest_data['provider']['name'] == 'virtualbox' and 'guest_additions' in manifest_data['provider']:
            manifest_data['provider']['guest_additions'] = self.build_settings['guest_additions']
        if 'apt_proxy' in self.build_settings:
            manifest_data.get('plugins', {})['apt_proxy'] = self.build_settings['apt_proxy']
        if 'ec2-credentials' in self.build_settings:
            if 'credentials' not in manifest_data['provider']:
                manifest_data['provider']['credentials'] = {}
            for key in ['access-key', 'secret-key', 'certificate', 'private-key', 'user-id']:
                if key in self.build_settings['ec2-credentials']:
                    manifest_data['provider']['credentials'][key] = self.build_settings['ec2-credentials'][key]
        if 's3-region' in self.build_settings and manifest_data['volume']['backing'] == 's3':
            if 'region' not in manifest_data['image']:
                manifest_data['image']['region'] = self.build_settings['s3-region']
        return manifest_data
