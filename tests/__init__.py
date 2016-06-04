

# Snatched from: http://stackoverflow.com/a/2186565/339505
def recursive_glob(path, pattern):
    import fnmatch
    import os
    for path, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(path, filename)
