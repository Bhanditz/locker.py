# locker.py
Metaclass that makes container classes behave as if they are empty until they are unlocked.

This project is new and under development. Features may not work exactly as documented and may change dramatically at any time.

# Logic
### ```Locker``` metaclass
The ```Locker``` metaclass takes every method from a class or its base clases (other than a select few such as ```__init__```) and applies the ```locker()``` decorator. By default, it does _not_ alter any of the methods of the actual class being defined, but it does alter the methods inherited from any of its base classes. It can be configured to alter the methods of the class being defined or any particular of the base classes.
### ```locker()``` decorator
The ```locker()``` decorator is best described by its docstring:

Decorator factory that decorates a method of a class that has inherited
one other class. It changes the method's behavior based on the "custom"
parameter, the state of the instance attribute "_locked", and the presense
of an identically named method in the base class.

When there is no method in the base class with the name of the decorated
function, this decorator has no effect.

_locked:
    - True: Depends on "custom" parameter:
        - True: Execute body of decorated function.
        - False: Execute base class's version of this method against an
               empty instance of the base class, return the result. There
               are no side effects.
    - False: Execute base class's version of this method against this
           instance, with any associated side effects to this instance.


# Usage
## Creating a Lockable Container
If you would just like to create something like a locking dictionary, this is all you need to do (python 3):
```python
class LockingDict(dict, metaclass=Locker):
    pass
```
Any methods created in that class will not be lockable unless you specify the ```lock``` class property like so
```python
class LockingDict(dict, metaclass=Locker):
    lock = {'bases', 'local'}
    
    def my_method():
        return 'hi'
```
In the above case, all methods (including my_method) will be locked upon instantiation. You can also specify individual base classes like ```'dict'``` instead of using ```'bases'``` to refer to all base classes.

Below, we specify only ```'local'```, which means none of the base class methods will be lockable, but all of the local methods (including ```my_method```) will be locked.
```python
class LockingDict(dict, metaclass=Locker):
    lock = {'bases', 'local'}
    
    def my_method():
        return 'hi'
```
The default value for ```lock``` if not specified is ```{'bases'}```.

## Using a Lockable Container
Instantiation of your locking container will require one additional parameter, ```req```. For example, instantiate a ```LockingDict``` like
```python
ld = LockingDict('key1', {'key1': 'v1', 'key2': 'v2})
```
Now if you try to access any key in your ```LockingDict```, you a ```KeyError``` will be raised until it is unlocked with the ```unlock()``` method. This method takes the ```req``` key and its respective value. To unlock the aforementioned ```LockingDict```, use
```python
ld.unlock('key1', 'v1')
```
This method returns a truth value indicating whether the container was successfully unlocked. Once unlocked, you can use it as a normal instance of the parent container class. For this example ```LockingDict```, no other arguments will successfully unlock it except those specified above. You can relock your container like so:
```python
ld.lock()
```

## Using the ```locker()``` Decorator
The ```locker()``` decorator can be used to individually make specific methods lockable. Should you want to create a locking dictionary with only some of its local methods lockable, you could write something like this:
```python
class LockingDict(dict, metaclass=Locker):
    def is_locked(self):
        return self._locked
    
    @locker(custom=True)
    def __getitem__(self, key):
        print('This container is locked!')
```
In the above case, we override ```dict.__getitem__``` with a local method. We set ```custom``` to ```True``` so we can define a custom action when the container is locked, otherwise the contents of ```__getitem__``` will be ignored and the method will behave as it would without the local method definition (since the default for ```lock``` is ```{'bases'}``` and ```__getitem``` is likewise already decorated). Now when we try to access a dictionary value, the message "This container is locked!" is printed instead of a ```KeyError``` being raised.

The way ```locker()``` works is by using the base class implementation when the container is unlocked, likewise it is not possible decorate methods that do not exist in one of the base classes. In the future, the implementation of ```locker()``` may change to allow decoration of any method, which will require a means to define the method's operation for both locked and unlocked states.
