"""Remote module containing methods to bootstrap remotely
"""
from Pyro4.util import SerializerBase
import logging
log = logging.getLogger(__name__)

supported_classes = ['bootstrapvz.base.manifest.Manifest',
                     'bootstrapvz.base.bootstrapinfo.BootstrapInformation',
                     'bootstrapvz.base.bootstrapinfo.DictClass',
                     'bootstrapvz.common.fs.loopbackvolume.LoopbackVolume',
                     'bootstrapvz.common.fs.qemuvolume.QEMUVolume',
                     'bootstrapvz.common.fs.virtualdiskimage.VirtualDiskImage',
                     'bootstrapvz.common.fs.virtualmachinedisk.VirtualMachineDisk',
                     'bootstrapvz.base.fs.partitionmaps.gpt.GPTPartitionMap',
                     'bootstrapvz.base.fs.partitionmaps.msdos.MSDOSPartitionMap',
                     'bootstrapvz.base.fs.partitionmaps.none.NoPartitions',
                     'bootstrapvz.base.fs.partitions.mount.Mount',
                     'bootstrapvz.base.fs.partitions.gpt.GPTPartition',
                     'bootstrapvz.base.fs.partitions.gpt_swap.GPTSwapPartition',
                     'bootstrapvz.base.fs.partitions.msdos.MSDOSPartition',
                     'bootstrapvz.base.fs.partitions.msdos_swap.MSDOSSwapPartition',
                     'bootstrapvz.base.fs.partitions.single.SinglePartition',
                     'bootstrapvz.base.fs.partitions.unformatted.UnformattedPartition',
                     'bootstrapvz.common.bytes.Bytes',
                     'bootstrapvz.common.sectors.Sectors',
                     ]

supported_exceptions = ['bootstrapvz.common.exceptions.ManifestError',
                        'bootstrapvz.common.exceptions.TaskListError',
                        'bootstrapvz.common.exceptions.TaskError',
                        'bootstrapvz.base.fs.exceptions.VolumeError',
                        'bootstrapvz.base.fs.exceptions.PartitionError',
                        'bootstrapvz.base.pkg.exceptions.PackageError',
                        'bootstrapvz.base.pkg.exceptions.SourceError',
                        'bootstrapvz.common.exceptions.UnitError',
                        'bootstrapvz.common.fsm_proxy.FSMProxyError',
                        'subprocess.CalledProcessError',
                        ]


def register_deserialization_handlers():
    for supported_class in supported_classes:
        SerializerBase.register_dict_to_class(supported_class, deserialize)
    for supported_exc in supported_exceptions:
        SerializerBase.register_dict_to_class(supported_exc, deserialize_exception)
    import subprocess
    SerializerBase.register_class_to_dict(subprocess.CalledProcessError, serialize_called_process_error)


def unregister_deserialization_handlers():
    for supported_class in supported_classes:
        SerializerBase.unregister_dict_to_class(supported_class, deserialize)
    for supported_exc in supported_exceptions:
        SerializerBase.unregister_dict_to_class(supported_exc, deserialize_exception)


def deserialize_exception(fq_classname, data):
    class_object = get_class_object(fq_classname)
    return SerializerBase.make_exception(class_object, data)


def deserialize(fq_classname, data):
    class_object = get_class_object(fq_classname)
    from Pyro4.util import SerpentSerializer
    from Pyro4.errors import SecurityError
    ser = SerpentSerializer()
    state = {}
    for key, value in data.items():
        try:
            state[key] = ser.recreate_classes(value)
        except SecurityError as e:
            msg = 'Unable to deserialize key `{key}\' on {class_name}'.format(key=key, class_name=fq_classname)
            raise Exception(msg, e)

    instance = class_object.__new__(class_object)
    instance.__setstate__(state)
    return instance


def serialize_called_process_error(obj):
    # This is by far the weirdest exception serialization.
    # There is a bug in both Pyro4 and the Python subprocess module.
    # CalledProcessError does not populate its args property,
    # although according to https://docs.python.org/2/library/exceptions.html#exceptions.BaseException.args
    # it should...
    # So we populate that property during serialization instead
    # (the code is grabbed directly from Pyro4's class_to_dict())
    # However, Pyro4 still cannot figure out to call the deserializer
    # unless we also use setattr() on the exception to set the args below
    # (before throwing it).
    # Mind you, the error "__init__() takes at least 3 arguments (2 given)"
    # is thrown *on the server* if we don't use setattr().
    # It's all very confusing to me and I'm not entirely
    # sure what the exact problem is. Regardless - it works, so there.
    return {'__class__': obj.__class__.__module__ + '.' + obj.__class__.__name__,
            '__exception__': True,
            'args': (obj.returncode, obj.cmd, obj.output),
            'attributes': vars(obj)  # add custom exception attributes
            }


def get_class_object(fq_classname):
    parts = fq_classname.split('.')
    module_name = '.'.join(parts[:-1])
    class_name = parts[-1]
    import importlib
    imported_module = importlib.import_module(module_name)
    return getattr(imported_module, class_name)
