from bootstrapvz.base import Task
from bootstrapvz.common import phases
import os


class CheckAssetsPath(Task):
    description = 'Checking whether the assets path exist'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.exceptions import TaskError
        assets = info.manifest.plugins['chef']['assets']
        if not os.path.exists(assets):
            msg = 'The assets directory {assets} does not exist.'.format(assets=assets)
            raise TaskError(msg)
        if not os.path.isdir(assets):
            msg = 'The assets path {assets} does not point to a directory.'.format(assets=assets)
            raise TaskError(msg)


class AddPackages(Task):
    description = 'Add chef package'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('chef')


class CopyChefAssets(Task):
    description = 'Copying chef assets'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import copy_tree
        copy_tree(info.manifest.plugins['chef']['assets'], os.path.join(info.root, 'etc/chef'))
