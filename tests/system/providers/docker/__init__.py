from contextlib import contextmanager
import logging
log = logging.getLogger(__name__)


@contextmanager
def boot_image(manifest, build_server, bootstrap_info):
    image_id = None
    try:
        import os
        from bootstrapvz.common.tools import log_check_call
        docker_machine = build_server.run_settings.get('docker', {}).get('machine', None)
        docker_env = os.environ.copy()
        if docker_machine is not None:
            cmd = ('eval "$(docker-machine env {machine})" && '
                   'echo $DOCKER_HOST && echo $DOCKER_CERT_PATH && echo $DOCKER_TLS_VERIFY'
                   .format(machine=docker_machine))
            [docker_host, docker_cert_path, docker_tls] = log_check_call([cmd], shell=True)
            docker_env['DOCKER_TLS_VERIFY'] = docker_tls
            docker_env['DOCKER_HOST'] = docker_host
            docker_env['DOCKER_CERT_PATH'] = docker_cert_path
            docker_env['DOCKER_MACHINE_NAME'] = docker_machine
        from bootstrapvz.remote.build_servers.local import LocalBuildServer
        image_id = bootstrap_info._docker['image_id']
        if not isinstance(build_server, LocalBuildServer):
            import tempfile
            handle, image_path = tempfile.mkstemp()
            os.close(handle)
            remote_image_path = os.path.join('/tmp', image_id)
            try:
                log.debug('Saving remote image to file')
                build_server.remote_command([
                    'sudo', 'docker', 'save',
                    '--output=' + remote_image_path,
                    image_id,
                ])
                log.debug('Downloading remote image')
                build_server.download(remote_image_path, image_path)
                log.debug('Importing image')
                log_check_call(['docker', 'load', '--input=' + image_path], env=docker_env)
            except (Exception, KeyboardInterrupt):
                raise
            finally:
                log.debug('Deleting exported image from build server and locally')
                build_server.delete(remote_image_path)
                os.remove(image_path)
                log.debug('Deleting image from build server')
                build_server.remote_command(['sudo', 'docker', 'rmi',
                                             bootstrap_info._docker['image_id']])

        from image import Image
        with Image(image_id, docker_env) as container:
            yield container
    finally:
        if image_id is not None:
            log.debug('Deleting image')
            log_check_call(['docker', 'rmi', image_id], env=docker_env)
