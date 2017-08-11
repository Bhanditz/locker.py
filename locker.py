def locker(custom=False):
	"""Decorator factory that decorates a method of a class that has inherited
	one other class. It changes the method's behavior based on the "custom"
	parameter, the state of the instance attribute "_locked", and the presense
	of an identically named method in the base class.
	
	* When there is no method in the base class with the name of the decorated
	function, this decorator has no effect.

	_locked:
		True: Depends on "custom" parameter:
			True: Execute body of decorated function.
			False: Execute base class's version of this method against an
				   empty instance of the base class, return the result. There
				   are no side effects.
		False: Execute base class's version of this method against this
			   instance, with any associated side effects to this instance.
	"""
	def decorator(f):
		def new_f(self, *args, **kwargs):
			try:
				base = self.__class__.__bases__[0]
				base_f = getattr(base, f.__name__)
				if self._locked:
					return (f if custom else base_f)(base(), *args, **kwargs)
			except AttributeError:
				return f(self, *args, **kwargs)
			return base_f(self, *args, **kwargs)
		return new_f
	return decorator


class Locker(type):
	""" Use this as a metaclass to create a container class that behaves as if
	it is empty until it is unlocked. This can only be used on classes with a
	__getitem__ method. Use this on a subclass of the container to lock.
	"""
	ignore = {'__getattribute__', '__new__', '__call__', '__subclasshook__',
			  '__init__', 'lock', 'unlock', '__init_subclass__'}

	def __new__(mcs, name, bases, local):
		base_class_names = set()
		classes_methods = []
		for base_class in bases:
			base_class_names.add(base_class.__name__)
			# Base methods: low priority
			classes_methods.append((base_class.__name__,
									mcs._get_methods(base_class)))
		classes_methods.append(('local', local))    # Locals: medium priority
		try:
			to_lock = local['lock']
			if 'bases' in to_lock:
				to_lock.remove('bases')
				to_lock |= base_class_names
		except KeyError:
			to_lock = base_class_names
		new_local = {}
		for class_name, methods in classes_methods:
			if class_name in to_lock:
				new_local.update(mcs._lock_methods(methods))
			else:
				new_local.update(methods)
		new_local.update(mcs._locking_methods())    # Locking: high priority
		return type.__new__(mcs, name, bases, new_local)

	@staticmethod
	def _get_methods(clss):
		return {mth_name: getattr(clss, mth_name) for mth_name in dir(clss)
				if callable(getattr(clss, mth_name)) and mth_name != '__class__'}
	
	@classmethod
	def _lock_methods(mcs, methods):
		locked_methods = {}
		for method_name, method in methods.items():
			if method_name not in mcs.ignore and callable(method):
				locked_methods[method_name] = locker()(method)
			else:
				locked_methods[method_name] = method
		return locked_methods
	
	@staticmethod
	def _locking_methods():
		methods = {}
		
		def __init__(self, req, *args, **kwargs):
			self.__class__.__bases__[0].__init__(self, *args, **kwargs)
			try:
				self.__class__.__bases__[0].__getitem__(self, req)
			except LookupError as e:
				key_index = e.__class__.__name__.rstrip('Error').lower()
				raise e.__class__('Provided {} must exist. '.format(key_index)
								  + 'This instance cannot be unlocked.')
			if hasattr(req, '__iter__'):
				self._req = set(req)
			else:
				self._req = {req}
			self._locked = True
		
		def lock(self):
			self._locked = True
		
		def unlock(self, key, value):
			if key in self._req and \
					self.__class__.__bases__[0].__getitem__(self, key) == value:
				self._locked = False
				return True
			return False
		
		methods['__init__'] = __init__
		methods['lock'] = lock
		methods['unlock'] = unlock
		return methods