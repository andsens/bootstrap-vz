

class FSMProxy(object):

	def __init__(self, cfg):
		from fysom import Fysom
		events = set([event['name'] for event in cfg['events']])
		cfg['callbacks'] = self.collect_event_listeners(events, cfg['callbacks'])
		self.fsm = Fysom(cfg)
		self.attach_proxy_methods(self.fsm, events)

	def collect_event_listeners(self, events, callbacks):
		callbacks = callbacks.copy()
		callback_names = []
		for event in events:
			callback_names.append(('_before_' + event, 'onbefore' + event))
			callback_names.append(('_after_' + event, 'onafter' + event))
		for fn_name, listener in callback_names:
			fn = getattr(self, fn_name, None)
			if callable(fn):
				if listener in callbacks:
					old_fn = callbacks[listener]

					def wrapper(e, old_fn=old_fn, fn=fn):
						old_fn(e)
						fn(e)
					callbacks[listener] = wrapper
				else:
					callbacks[listener] = fn
		return callbacks

	def attach_proxy_methods(self, fsm, events):
		def make_proxy(fsm, event):
			fn = getattr(fsm, event)

			def proxy(*args, **kwargs):
				if len(args) > 0:
					raise FSMProxyError('FSMProxy event listeners only accept named arguments.')
				fn(**kwargs)
			return proxy

		for event in events:
			if not hasattr(self, event):
				setattr(self, event, make_proxy(fsm, event))


class FSMProxyError(Exception):
	pass
