import os
import subprocess
import time
import logging


def pull(info, images, retries=10):
  if len(images) == 0:
    return

  bin_docker = os.path.join(info.root, 'usr/bin/docker')
  graph_dir = os.path.join(info.root, 'var/lib/docker')
  socket = 'unix://' + os.path.join(info.workspace, 'docker.sock')
  pidfile = os.path.join(info.workspace, 'docker.pid')
  try:
    daemon = subprocess.Popen([bin_docker, '-d', '--graph', graph_dir, '-H', socket, '-p', pidfile])
    for _ in range(retries):
      if subprocess.call([bin_docker, '-H', socket, 'version']) == 0:
        break
      time.sleep(1)
    for img in images:
      if img.endswith('.tar.gz') or img.endswith('.tgz'):
        cmd = [bin_docker, '-H', socket, 'load', '-i', img]
        logging.debug(' '.join(cmd))
        if subprocess.call(cmd) != 0:
          msg = 'error loading docker image {img}.'.format(img=img)
          raise Exception(msg)
        continue
      cmd = [bin_docker, '-H', socket, 'pull', img]
      logging.debug('running: %s', ' '.join(cmd))
      if subprocess.call(cmd) != 0:
        msg = 'error pulling docker image {img}.'.format(img=img)
        raise Exception(msg)
  finally:
    daemon.terminate()

if __name__ == '__main__':
  class Info(object):
    root = '/tmp/bootstrap-vz/root'
    workspace = '/tmp/bootstrap-vz/workspace'

  pull_images = ['/usr/local/google/home/proppy/bootstrap-vz/busybox.tar.gz', 'golang:1.3']
  pull(Info(), pull_images)
