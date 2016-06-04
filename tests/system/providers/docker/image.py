from bootstrapvz.common.tools import log_check_call
import logging
log = logging.getLogger(__name__)


class Image(object):

    def __init__(self, image_id, docker_env):
        self.image_id = image_id
        self.docker_env = docker_env

    def __enter__(self):
        self.container = Container(self.image_id, self.docker_env)
        self.container.create()
        try:
            self.container.start()
        except:
            self.container.destroy()
            raise
        return self.container

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.container.stop()
            self.container.destroy()
        except Exception as e:
            log.exception(e)


class Container(object):

    def __init__(self, image_id, docker_env):
        self.image_id = image_id
        self.docker_env = docker_env

    def create(self):
        log.debug('Creating container')
        [self.container_id] = log_check_call(['docker', 'create', '--tty=true', self.image_id], env=self.docker_env)

    def start(self):
        log.debug('Starting container')
        log_check_call(['docker', 'start', self.container_id], env=self.docker_env)

    def run(self, command):
        log.debug('Running command in container')
        return log_check_call(['docker', 'exec', self.container_id] + command, env=self.docker_env)

    def stop(self):
        log.debug('Stopping container')
        log_check_call(['docker', 'stop', self.container_id], env=self.docker_env)

    def destroy(self):
        log.debug('Deleting container')
        log_check_call(['docker', 'rm', self.container_id], env=self.docker_env)
        del self.container_id
