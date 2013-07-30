#!/bin/bash

echo "Copy public ssh keys to authorized_keys"
for f in /mnt/*.pub
do
  cat $f >> /root/.ssh/authorized_keys

done
