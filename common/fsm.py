

def attach_proxy_methods(obj, events, fsm):
	methods = set([e['name'] for e in events])
	for event in methods:
		if not hasattr(obj, event):
			setattr(obj, event, lambda e=event: getattr(fsm, e)())
