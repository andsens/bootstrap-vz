from contextlib import contextmanager


def get_partitions():
    import re
    regexp = re.compile(r'^ *(?P<major>\d+) *(?P<minor>\d+) *(?P<num_blks>\d+) (?P<dev_name>\S+)$')
    matches = {}
    path = '/proc/partitions'
    with open(path) as partitions:
        next(partitions)
        next(partitions)
        for line in partitions:
            match = regexp.match(line)
            if match is None:
                raise RuntimeError('Unable to parse {line} in {path}'.format(line=line, path=path))
            matches[match.group('dev_name')] = match.groupdict()
    return matches


@contextmanager
def unmounted(volume):
    from bootstrapvz.base.fs.partitionmaps.none import NoPartitions

    p_map = volume.partition_map
    root_dir = p_map.root.mount_dir
    p_map.root.unmount()
    if not isinstance(p_map, NoPartitions):
        p_map.unmap(volume)
        yield
        p_map.map(volume)
    else:
        yield
    p_map.root.mount(destination=root_dir)
