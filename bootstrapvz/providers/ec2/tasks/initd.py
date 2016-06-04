from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import initd
from . import assets
import os.path


class AddEC2InitScripts(Task):
    description = 'Adding EC2 startup scripts'
    phase = phases.system_modification
    successors = [initd.InstallInitScripts]

    @classmethod
    def run(cls, info):
        init_scripts = {'ec2-get-credentials': 'ec2-get-credentials',
                        'ec2-run-user-data': 'ec2-run-user-data'}

        init_scripts_dir = os.path.join(assets, 'init.d')
        for name, path in init_scripts.iteritems():
            info.initd['install'][name] = os.path.join(init_scripts_dir, path)
