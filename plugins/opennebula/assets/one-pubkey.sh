#!/bin/bash

echo "Reconfigure host ssh keys"
dpkg-reconfigure openssh-server

if [ ! -e /root/.ssh ]; then
  mkdir /root/.ssh
  touch /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
fi

echo "Copy public ssh keys to authorized_keys"
for f in /mnt/*.pub
do
  cat $f >> /root/.ssh/authorized_keys

done
