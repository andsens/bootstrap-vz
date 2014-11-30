"""Remote module containing methods to bootstrap remotely
"""


def register_deserialization_handlers():
	from Pyro4.util import SerializerBase
	SerializerBase.register_dict_to_class('bootstrapvz.base.manifest.Manifest', deserialize_manifest)
	SerializerBase.register_dict_to_class('bootstrapvz.base.bootstrapinfo.BootstrapInformation', deserialize_bootstrapinfo)


def unregister_deserialization_handlers():
	from Pyro4.util import SerializerBase
	SerializerBase.unregister_dict_to_class('bootstrapvz.base.manifest.Manifest')
	SerializerBase.unregister_dict_to_class('bootstrapvz.base.bootstrapinfo.BootstrapInformation')


def deserialize_manifest(classname, state):
	from bootstrapvz.base.manifest import Manifest
	return Manifest(path=state['path'], data=state['data'])


def deserialize_bootstrapinfo(classname, state):
	from bootstrapvz.base.bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation.__new__(BootstrapInformation)
	bootstrap_info.__setstate__(state)
	return bootstrap_info
