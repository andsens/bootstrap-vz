"""Remote module containing methods to bootstrap remotely
"""
import bootstrapvz.common.exceptions


def register_deserialization_handlers():
	from Pyro4.util import SerializerBase
	SerializerBase.register_dict_to_class('bootstrapvz.base.manifest.Manifest', deserialize_manifest)
	SerializerBase.register_dict_to_class('bootstrapvz.base.bootstrapinfo.BootstrapInformation', deserialize_bootstrapinfo)
	SerializerBase.register_dict_to_class('bootstrapvz.common.exceptions.ManifestError', deserialize_exception)
	SerializerBase.register_dict_to_class('bootstrapvz.common.exceptions.TaskListError', deserialize_exception)
	SerializerBase.register_dict_to_class('bootstrapvz.common.exceptions.TaskError', deserialize_exception)


def unregister_deserialization_handlers():
	from Pyro4.util import SerializerBase
	SerializerBase.unregister_dict_to_class('bootstrapvz.base.manifest.Manifest')
	SerializerBase.unregister_dict_to_class('bootstrapvz.base.bootstrapinfo.BootstrapInformation')
	SerializerBase.unregister_dict_to_class('bootstrapvz.common.exceptions.ManifestError')
	SerializerBase.unregister_dict_to_class('bootstrapvz.common.exceptions.TaskListError')
	SerializerBase.unregister_dict_to_class('bootstrapvz.common.exceptions.TaskError')


def deserialize_manifest(classname, state):
	from bootstrapvz.base.manifest import Manifest
	manifest = Manifest.__new__(Manifest)
	manifest.__setstate__(state)
	return manifest


def deserialize_bootstrapinfo(classname, state):
	from bootstrapvz.base.bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation.__new__(BootstrapInformation)
	bootstrap_info.__setstate__(state)
	return bootstrap_info

deserialize_map = {'bootstrapvz.common.exceptions.ManifestError': bootstrapvz.common.exceptions.ManifestError,
                   'bootstrapvz.common.exceptions.TaskListError': bootstrapvz.common.exceptions.TaskListError,
                   'bootstrapvz.common.exceptions.TaskError': bootstrapvz.common.exceptions.TaskError,
                   }


def deserialize_exception(classname, data):
	from Pyro4.util import SerializerBase
	return SerializerBase.make_exception(deserialize_map[classname], data)
