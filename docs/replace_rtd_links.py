
def setup(app):
	app.connect('doctree-resolved', replace_rtd_links)

	return {'version': '0.1'}


def replace_rtd_links(app, doctree, fromdocname):
	from docutils import nodes
	import re

	rtd_baseurl = 'http://bootstrap-vz.readthedocs.org/en/master/'
	search = re.compile('^' + re.escape(rtd_baseurl) + '(.*)$')
	for node in doctree.traverse(nodes.reference):
		if 'refuri' not in node:
			continue
		if not node['refuri'].startswith(rtd_baseurl):
			continue
		node['refuri'] = re.sub(search, r'\1', node['refuri'])
