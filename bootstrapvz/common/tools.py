import os


def log_check_call(command, stdin=None, env=None, shell=False, cwd=None):
    status, stdout, stderr = log_call(command, stdin, env, shell, cwd)
    from subprocess import CalledProcessError
    if status != 0:
        e = CalledProcessError(status, ' '.join(command), '\n'.join(stderr))
        # Fix Pyro4's fixIronPythonExceptionForPickle() by setting the args property,
        # even though we use our own serialization (at least I think that's the problem).
        # See bootstrapvz.remote.serialize_called_process_error for more info.
        setattr(e, 'args', (status, ' '.join(command), '\n'.join(stderr)))
        raise e
    return stdout


def log_call(command, stdin=None, env=None, shell=False, cwd=None):
    import subprocess
    import logging
    from multiprocessing.dummy import Pool as ThreadPool
    from os.path import realpath

    command_log = realpath(command[0]).replace('/', '.')
    log = logging.getLogger(__name__ + command_log)
    if type(command) is list:
        log.debug('Executing: {command}'.format(command=' '.join(command)))
    else:
        log.debug('Executing: {command}'.format(command=command))

    process = subprocess.Popen(args=command, env=env, shell=shell, cwd=cwd,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    if stdin is not None:
        log.debug('  stdin: ' + stdin)
        process.stdin.write(stdin + "\n")
        process.stdin.flush()
    process.stdin.close()

    stdout = []
    stderr = []

    def handle_stdout(line):
        log.debug(line)
        stdout.append(line)

    def handle_stderr(line):
        log.error(line)
        stderr.append(line)

    handlers = {process.stdout: handle_stdout,
                process.stderr: handle_stderr}

    def stream_readline(stream):
        for line in iter(stream.readline, ''):
            handlers[stream](line.strip())

    pool = ThreadPool(2)
    pool.map(stream_readline, [process.stdout, process.stderr])
    pool.close()
    pool.join()
    process.wait()
    return process.returncode, stdout, stderr


def sed_i(file_path, pattern, subst, expected_replacements=1):
    replacement_count = inline_replace(file_path, pattern, subst)
    if replacement_count != expected_replacements:
        from exceptions import UnexpectedNumMatchesError
        msg = ('There were {real} instead of {expected} matches for '
               'the expression `{exp}\' in the file `{path}\''
               .format(real=replacement_count, expected=expected_replacements,
                       exp=pattern, path=file_path))
        raise UnexpectedNumMatchesError(msg)


def inline_replace(file_path, pattern, subst):
    import fileinput
    import re
    replacement_count = 0
    for line in fileinput.input(files=file_path, inplace=True):
        (replacement, count) = re.subn(pattern, subst, line)
        replacement_count += count
        print replacement,
    return replacement_count


def load_json(path):
    import json
    from minify_json import json_minify
    with open(path) as stream:
        return json.loads(json_minify(stream.read(), False))


def load_yaml(path):
    import yaml
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def load_data(path):
    filename, extension = os.path.splitext(path)
    if not os.path.isfile(path):
        raise Exception('The path {path} does not point to a file.'.format(path=path))
    if extension == '.json':
        return load_json(path)
    elif extension == '.yml' or extension == '.yaml':
        return load_yaml(path)
    else:
        raise Exception('Unrecognized extension: {ext}'.format(ext=extension))


def config_get(path, config_path):
    config = load_data(path)
    for key in config_path:
        config = config.get(key)
    return config


def copy_tree(from_path, to_path):
    from shutil import copy
    for abs_prefix, dirs, files in os.walk(from_path):
        prefix = os.path.normpath(os.path.relpath(abs_prefix, from_path))
        for path in dirs:
            full_path = os.path.join(to_path, prefix, path)
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    continue
                else:
                    os.remove(full_path)
            os.mkdir(full_path)
        for path in files:
            copy(os.path.join(abs_prefix, path),
                 os.path.join(to_path, prefix, path))


def rel_path(base, path):
    import os.path
    return os.path.normpath(os.path.join(os.path.dirname(base), path))
