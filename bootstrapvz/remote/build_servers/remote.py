from build_server import BuildServer
from bootstrapvz.common.tools import log_check_call
from contextlib import contextmanager
import logging
log = logging.getLogger(__name__)


class RemoteBuildServer(BuildServer):

    def __init__(self, name, settings):
        super(RemoteBuildServer, self).__init__(name, settings)
        self.address = settings['address']
        self.port = settings['port']
        self.username = settings['username']
        self.password = settings.get('password', None)
        self.keyfile = settings['keyfile']
        self.server_bin = settings['server_bin']

    @contextmanager
    def connect(self):
        with self.spawn_server() as forwards:
            args = {'listen_port': forwards['local_callback_port'],
                    'remote_port': forwards['remote_callback_port']}
            from callback import CallbackServer
            with CallbackServer(**args) as callback_server:
                with connect_pyro('localhost', forwards['local_server_port']) as connection:
                    connection.set_callback_server(callback_server)
                    yield connection

    @contextmanager
    def spawn_server(self):
        from . import getNPorts
        # We can't use :0 for the forwarding ports because
        # A: It's quite hard to retrieve the port on the remote after the daemon has started
        # B: SSH doesn't accept 0:localhost:0 as a port forwarding option
        [local_server_port, local_callback_port] = getNPorts(2)
        [remote_server_port, remote_callback_port] = getNPorts(2)

        server_cmd = ['sudo', self.server_bin, '--listen', str(remote_server_port)]

        def set_process_group():
            # Changes the process group of a command so that any SIGINT
            # for the main thread will not be propagated to it.
            # We'd like to handle SIGINT ourselves (i.e. propagate the shutdown to the serverside)
            import os
            os.setpgrp()

        addr_arg = '{user}@{host}'.format(user=self.username, host=self.address)
        ssh_cmd = ['ssh', '-i', self.keyfile,
                          '-p', str(self.port),
                          '-L' + str(local_server_port) + ':localhost:' + str(remote_server_port),
                          '-R' + str(remote_callback_port) + ':localhost:' + str(local_callback_port),
                          addr_arg]
        full_cmd = ssh_cmd + ['--'] + server_cmd

        log.debug('Opening SSH connection to build server `{name}\''.format(name=self.name))
        import sys
        import subprocess
        ssh_process = subprocess.Popen(args=full_cmd, stdout=sys.stderr, stderr=sys.stderr,
                                       preexec_fn=set_process_group)
        try:
            yield {'local_server_port': local_server_port,
                   'local_callback_port': local_callback_port,
                   'remote_server_port': remote_server_port,
                   'remote_callback_port': remote_callback_port}
        finally:
            log.debug('Waiting for SSH connection to the build server to close')
            import time
            start = time.time()
            while ssh_process.poll() is None:
                if time.time() - start > 5:
                    log.debug('Forcefully terminating SSH connection to the build server')
                    ssh_process.terminate()
                    break
                else:
                    time.sleep(0.5)

    def download(self, src, dst):
        log.debug('Downloading file `{src}\' from '
                  'build server `{name}\' to `{dst}\''
                  .format(src=src, dst=dst, name=self.name))
        # Make sure we can read the file as {user}
        self.remote_command(['sudo', 'chown', self.username, src])
        src_arg = '{user}@{host}:{path}'.format(user=self.username, host=self.address, path=src)
        log_check_call(['scp', '-i', self.keyfile, '-P', str(self.port),
                        src_arg, dst])

    def delete(self, path):
        log.debug('Deleting file `{path}\' on build server `{name}\''.format(path=path, name=self.name))
        self.remote_command(['sudo', 'rm', path])

    def remote_command(self, command):
        ssh_cmd = ['ssh', '-i', self.keyfile,
                          '-p', str(self.port),
                          self.username + '@' + self.address,
                          '--'] + command
        log_check_call(ssh_cmd)


@contextmanager
def connect_pyro(host, port):
    import Pyro4
    server_uri = 'PYRO:server@{host}:{port}'.format(host=host, port=port)
    connection = Pyro4.Proxy(server_uri)

    log.debug('Connecting to RPC daemon')

    connected = False
    try:
        remaining_retries = 5
        while not connected:
            try:
                connection.ping()
                connected = True
            except (Pyro4.errors.ConnectionClosedError, Pyro4.errors.CommunicationError):
                if remaining_retries > 0:
                    remaining_retries -= 1
                    from time import sleep
                    sleep(2)
                else:
                    raise

        yield connection
    finally:
        if connected:
            log.debug('Stopping RPC daemon')
            connection.stop()
            connection._pyroRelease()
        else:
            log.warn('Unable to stop RPC daemon, it might still be running on the server')
