"""Main module containing all the setup necessary for running the remote bootstrapping process
"""


def main():
    """Main function for invoking the bootstrap process remotely
    """
    # Get the commandline arguments
    opts = get_opts()

    from bootstrapvz.common.tools import load_data
    # load the manifest data, we might want to modify it later on
    manifest_data = load_data(opts['MANIFEST'])

    # load the build servers file
    build_servers = load_data(opts['--servers'])
    # Pick a build server
    from build_servers import pick_build_server
    preferences = {}
    if opts['--name'] is not None:
        preferences['name'] = opts['--name']
    if opts['--release'] is not None:
        preferences['release'] = opts['--release']
    build_server = pick_build_server(build_servers, manifest_data, preferences)

    # Apply the build server settings to the manifest (e.g. the virtualbox guest additions path)
    manifest_data = build_server.apply_build_settings(manifest_data)

    # Load the manifest
    from bootstrapvz.base.manifest import Manifest
    manifest = Manifest(path=opts['MANIFEST'], data=manifest_data)

    # Set up logging
    from bootstrapvz.base.main import setup_loggers
    setup_loggers(opts)

    # Register deserialization handlers for objects
    # that will pass between server and client
    from . import register_deserialization_handlers
    register_deserialization_handlers()

    # Everything has been set up, connect to the server and begin the bootstrapping process
    with build_server.connect() as connection:
        connection.run(manifest,
                       debug=opts['--debug'],
                       dry_run=opts['--dry-run'])


def get_opts():
    """Creates an argument parser and returns the arguments it has parsed
    """
    from docopt import docopt
    usage = """bootstrap-vz-remote

Usage: bootstrap-vz-remote [options] --servers=<path> MANIFEST

Options:
  --servers <path>    Path to list of build servers
  --name <name>       Selects specific server from the build servers list
  --release <release> Require the build server OS to be a specific release
  --log <path>        Log to given directory [default: /var/log/bootstrap-vz]
                      If <path> is `-' file logging will be disabled.
  --pause-on-error    Pause on error, before rollback
  --dry-run           Don't actually run the tasks
  --color=auto|always|never
                     Colorize the console output [default: auto]
  --debug             Print debugging information
  -h, --help          show this help
    """
    return docopt(usage)
