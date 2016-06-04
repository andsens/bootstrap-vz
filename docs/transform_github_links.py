import re


def setup(app):
    app.connect('doctree-resolved', transform_github_links)
    return {'version': '0.1'}

# Maps from files in docs/ to folders/files in repo
includes_mapping = {
    r'^index$': r'',
    r'^(providers|plugins)/index$': r'bootstrapvz/\1/',
    r'^(providers|plugins)/(?!index)([^/]+)$': r'bootstrapvz/\1/\2/',
    r'^manifests/index$': r'manifest/',
    r'^manifests/official_([^_]+)_manifests$': r'manifest/official/\1/',
    r'^testing/index$': r'tests/',
    r'^testing/(?!index)([^/]+)_tests$': r'tests/\1/',
    r'^remote_bootstrapping$': r'bootstrapvz/remote/',
    r'^developers/index$': r'bootstrapvz/',
    r'^developers/contributing$': r'CONTRIBUTING.rst',
    r'^developers/documentation$': r'docs/',
    r'^changelog$': r'CHANGELOG.rst',
}


# Maps from links in repo to files/folders in docs/
links_mapping = {
    r'^$': r'',
    r'^bootstrapvz/(providers|plugins)$': r'\1',
    r'^bootstrapvz/(providers|plugins)/([^/]+)$': r'\1/\2.html',
    r'^tests$': r'testing',
    r'^manifests$': r'manifests',
    r'^manifests/official/([^/]+)$': r'manifests/official_\1_manifests.html',
    r'^tests/([^/]+)$': r'testing/\1_tests.html',
    r'^bootstrapvz/remote$': r'remote_bootstrapping.html',
    r'^bootstrapvz$': r'developers',
    r'^CONTRIBUTING\.rst$': r'developers/contributing.html',
    r'^docs$': r'developers/documentation.html',
    r'^CHANGELOG\.rst$': r'changelog.html',
}

for key, val in includes_mapping.items():
    del includes_mapping[key]
    includes_mapping[re.compile(key)] = val

for key, val in links_mapping.items():
    del links_mapping[key]
    links_mapping[re.compile(key)] = val


def find_original(path):
    for key, val in includes_mapping.items():
        if re.match(key, path):
            return re.sub(key, val, path)
    return None


def find_docs_link(link):
    try:
        # Preserve anchor when doing lookups
        link, anchor = link.split('#', 1)
        anchor = '#' + anchor
    except ValueError:
        # No anchor, keep the original link
        anchor = ''
    for key, val in links_mapping.items():
        if re.match(key, link):
            return re.sub(key, val, link) + anchor
    return None


def transform_github_links(app, doctree, fromdocname):
    # Convert relative links in repo into relative links in docs.
    # We do this by first figuring out whether the current document
    # has been included from outside docs/ and only continue if so.
    # Next we take the repo path matching the current document
    # (lookup through 'includes_mapping'), tack the link onto the dirname
    # of that path and normalize it using os.path.normpath.
    # The result is the path to a document/folder in the repo.
    # We then convert this path into one that works in the documentation
    # (lookup through 'links_mapping').
    # If a mapping is found we, create a relative link from the current document.

    from docutils import nodes
    import os.path
    original_path = find_original(fromdocname)
    if original_path is None:
        return

    for node in doctree.traverse(nodes.reference):
        if 'refuri' not in node:
            continue
        if node['refuri'].startswith('http'):
            continue
        abs_link = os.path.normpath(os.path.join(os.path.dirname(original_path), node['refuri']))
        docs_link = find_docs_link(abs_link)
        if docs_link is None:
            continue
        # special handling for when we link inside the same document
        if docs_link.startswith('#'):
            node['refuri'] = docs_link
        else:
            node['refuri'] = os.path.relpath(docs_link, os.path.dirname(fromdocname))
