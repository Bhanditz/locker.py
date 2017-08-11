# locker.py
Metaclass that makes container classes behave as if they are empty until they are unlocked.

# Logic
### ```Locker``` metaclass
The ```Locker``` metaclass takes every method from an inherited class other than a select few (such as ```__init__```) and applies the ```locker()``` decorator. It does _not_ alter any of the methods of the actual class being defined, only the methods inherited from its base classes.
### ```locker()``` decorator
The ```locker()``` decorator makes a method return what it would return if the container were empty. It prevents the method from making any changes to the container.

# Usage
## Creation
If you would just like to create something like a locking dictionary, this is all you need to do (python 3):
```python
class LockingDict(dict, metaclass=Locker): pass
```

If you would like to lock a custom container, first you should create your regular container class, then you should subclass it and use the metaclass for that subclass. The subclass will be a locking version of that container. Methods of the subclass will not be locked. If you would like to specify individual functions as lockable, you can manually apply the ```locker()``` decorator like so:
```python
class MyContainer:
    def __init__(self, values):
        self.values = [i for i in values]

    def normal_method(self):
        return 'normal'

    @Locker.locker
    def __getitem__(self, index):
        return return self.values[index]
```

Now your ```__getitem__``` method will behave as a lockable method, but no other methods will unless they are explicitly locked with the decorator.

## Using a Locking Container
Instantiation of your locking container will require one additional parameter, ```req```. For example, instantiate a ```LockingDict``` like
```python
ld = LockingDict('key1', {'key1': 'v1', 'key2': 'v2})
```
Now if you try to access any key in your ```LockingDict```, you will get a keyerror until it is unlocked with the ```unlock()``` method. This method takes the ```req``` key and its respective value. To unlock the aforementioned ```LockingDict```, use
```python
ld.unlock('key1', 'v1')
```
This method returns a truth value indicating whether the container was successfully unlocked. Once unlocked, you can use it as a normal instance of the parent container class. For this example ```LockingDict```, no other arguments will successfully unlock it except those specified above. You can relock your container like so:
```python
ld.lock()
```
