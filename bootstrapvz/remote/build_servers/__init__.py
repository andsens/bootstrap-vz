

def pick_build_server(build_servers, manifest, preferences={}):
    # Validate the build servers list
    from bootstrapvz.common.tools import load_data, rel_path

    schema = load_data(rel_path(__file__, 'build-servers-schema.yml'))
    import jsonschema
    jsonschema.validate(build_servers, schema)

    if manifest['provider']['name'] == 'ec2':
        must_bootstrap = 'ec2-' + manifest['volume']['backing']
    else:
        must_bootstrap = manifest['provider']['name']

    def matches(name, settings):
        if preferences.get('name', name) != name:
            return False
        if preferences.get('release', settings['release']) != settings['release']:
            return False
        if must_bootstrap not in settings['can_bootstrap']:
            return False
        return True

    for name, settings in build_servers.iteritems():
        if not matches(name, settings):
            continue
        if settings['type'] == 'local':
            from local import LocalBuildServer
            return LocalBuildServer(name, settings)
        else:
            from remote import RemoteBuildServer
            return RemoteBuildServer(name, settings)
    raise Exception('Unable to find a build server that matches your preferences.')


def getNPorts(n, port_range=(1024, 65535)):
    import random
    ports = []
    for i in range(0, n):
        while True:
            port = random.randrange(*port_range)
            if port not in ports:
                ports.append(port)
                break
    return ports
