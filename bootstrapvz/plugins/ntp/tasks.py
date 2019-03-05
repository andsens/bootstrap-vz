from __future__ import print_function

from bootstrapvz.base import Task
from bootstrapvz.common import phases


class AddNtpPackage(Task):
    description = 'Adding NTP Package'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('ntp')


class SetNtpServers(Task):
    description = 'Setting NTP servers'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import fileinput
        import os
        import re
        ntp_path = os.path.join(info.root, 'etc/ntp.conf')
        servers = list(info.manifest.plugins['ntp']['servers'])
        debian_ntp_server = re.compile(r'.*[0-9]\.debian\.pool\.ntp\.org.*')
        for line in fileinput.input(files=ntp_path, inplace=True):
            # Will write all the specified servers on the first match, then supress all other default servers
            if re.match(debian_ntp_server, line):
                while servers:
                    print('server {server_address} iburst'.format(server_address=servers.pop(0)))
            else:
                print(line, end='')
