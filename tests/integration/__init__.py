import os.path
from bootstrapvz.common.tools import load_data

combine_manifests_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'manifests')
manifests = {'base': load_data(os.path.join(combine_manifests_path, 'base.yml')),
             'partitioned': load_data(os.path.join(combine_manifests_path, 'partitioned.yml')),
             'unpartitioned': load_data(os.path.join(combine_manifests_path, 'unpartitioned.yml')),
             }
build_settings = load_data(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'build_settings.yml'))
