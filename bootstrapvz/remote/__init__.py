"""Remote module containing methods to bootstrap remotely
"""
from Pyro4.util import SerializerBase
import logging
log = logging.getLogger(__name__)

supported_classes = ['bootstrapvz.base.manifest.Manifest',
                     'bootstrapvz.base.bootstrapinfo.BootstrapInformation',
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
                     'bootstrapvz.base.fs.partitions.gap.PartitionGap',
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
                        'bootstrapvz.common.bytes.UnitError',
                        'bootstrapvz.common.fsm_proxy.FSMProxyError',
                        ]


def register_deserialization_handlers():
	for supported_class in supported_classes:
		SerializerBase.register_dict_to_class(supported_class, deserialize)
	for supported_exc in supported_exceptions:
		SerializerBase.register_dict_to_class(supported_exc, deserialize_exception)


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
			import pprint
			msg += pprint.pformat(data)
			raise Exception(msg, e)

	instance = class_object.__new__(class_object)
	instance.__setstate__(state)
	return instance


def get_class_object(fq_classname):
	parts = fq_classname.split('.')
	module_name = '.'.join(parts[:-1])
	class_name = parts[-1]
	import importlib
	imported_module = importlib.import_module(module_name)
	return getattr(imported_module, class_name)
