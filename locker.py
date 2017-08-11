class Locker(type):
	""" Use this as a metaclass to create a container class that behaves as if
	it is empty until it is unlocked. This can only be used on classes with a
	__getitem__ method. Use this on a subclass of the container to lock.
	"""
	def __new__(cls, name, bases, local):
		new_local = {}
		
		def __init__(self, req, *args, **kwargs):
			self.__class__.__bases__[0].__init__(self, *args, **kwargs)
			try:
				self.__class__.__bases__[0].__getitem__(self, req)
			except LookupError as e:
				raise e.__class__('Provided index must exist. This instance'
								 ' cannot be unlocked.')
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
		
		for base in bases:
			for method_name, method in inspect.getmembers(base):
				if callable(method) and method_name not in \
						('__getattribute__', '__new__', '__call__',
						 '__subclasshook__', '__class__', '__init__', 'lock',
						 'unlock', '__init_subclass__'):
					new_local[method_name] = cls.locker(method)
		new_local.update(local)
		new_local['__init__'] = __init__
		new_local['lock'] = lock
		new_local['unlock'] = unlock
		return type.__new__(cls, name, bases, new_local)
	
	@staticmethod
	def locker(f):
		def new_f(self, *args, **kwargs):
			try:
				base = self.__class__.__bases__[0]
				base_f = getattr(base, f.__name__)
				if self._locked:
					return base_f(base(), *args, **kwargs)
			except AttributeError:
				return f(self, *args, **kwargs)
			return base_f(self, *args, **kwargs)
		return new_f
