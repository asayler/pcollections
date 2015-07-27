# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###

import redis

import keyval
import abc_base


### Constants ###

_SEP_FIELD = ':'
_PREFIX_STRING = "string"
_PREFIX_LIST = "list"
_PREFIX_SET = "set"
_PREFIX_MAPPING = "hash"
_INDEX_KEY = "_obj_index"


### Driver ###

class Driver(redis.StrictRedis):

    pass


### Base Objects ###

class Persistent(abc_base.Persistent):

    def _register(self, pipe):
        """Register Object as Existing"""

        pipe.sadd(_INDEX_KEY, self._redis_key)

    def _unregister(self, pipe):
        """Unregister Object as Existing"""

        pipe.srem(_INDEX_KEY, self._redis_key)

    def _exists(self, pipe):
        """Check if Object Exists (Immediate)"""

        return bool(pipe.sismember(_INDEX_KEY, self._redis_key))

    def exists(self):
        """Check if Object Exists (Transaction)"""

        # Exists Transaction
        def atomic_exists(pipe):

            pipe.multi()
            pipe.sismember(_INDEX_KEY, self._redis_key)

        # Check if Object Exists
        ret = self._driver.transaction(atomic_exists, self._redis_key)

        # Return Bool
        return bool(ret[0])

    def rem(self, force=False):
        """Delete Object"""

        # Delete Transaction
        def atomic_rem(pipe):

            if not self._exists(pipe):
                if force:
                    return
                else:
                    raise keyval.ObjectDNE(self)
            pipe.multi()
            pipe.delete(self._redis_key)
            self._unregister(pipe)

        # Delete Object
        self._driver.transaction(atomic_rem, self._redis_key)

class Mutable(Persistent, abc_base.Mutable):
    pass

class Container(Persistent, abc_base.Container):
    pass

class Iterable(Persistent, abc_base.Iterable):
    pass

class Sized(Persistent, abc_base.Sized):
    pass

class Sequence(Container, Iterable, Sized, abc_base.Sequence):
    pass

class MutableSequence(Mutable, Sequence, abc_base.MutableSequence):
    pass

class BaseSet(Container, Iterable, Sized, abc_base.BaseSet):
    pass

class MutableBaseSet(Mutable, BaseSet, abc_base.MutableBaseSet):
    pass

class Mapping(Container, Iterable, Sized, abc_base.Mapping):
    pass

class MutableMapping(Mutable, Mapping, abc_base.MutableMapping):
    pass

### Objects ###

class String(Sequence, abc_base.String):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(String, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_STRING, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise keyval.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return str(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        if val is None:
            raise TypeError("val must not be None")
        val = str(val)

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise keyval.ObjectExists(self)
            if not create and not exists:
                raise keyval.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.set(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableString(MutableSequence, String, abc_base.MutableString):
    pass

class List(Sequence, abc_base.List):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(List, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_LIST, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise keyval.ObjectDNE(self)
            pipe.multi()
            pipe.lrange(self._redis_key, 0, -1)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return list(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = list(val)
        types = set([type(v) for v in val])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in seq".format(typ))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise keyval.ObjectExists(self)
            if not create and not exists:
                raise keyval.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.rpush(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableList(MutableSequence, List, abc_base.MutableList):
    pass

class Set(BaseSet, abc_base.Set):

    def __init__(self, driver, key):
        """Set Constructor"""

        # Call Parent
        super(Set, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_SET, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise keyval.ObjectDNE(self)
            pipe.multi()
            pipe.smembers(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return set(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = set(val)
        types = set([type(v) for v in val])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in set".format(typ))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise keyval.ObjectExists(self)
            if not create and not exists:
                raise keyval.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableSet(MutableBaseSet, Set, abc_base.MutableSet):

    pass

class Dictionary(Mapping, abc_base.Dictionary):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(Dictionary, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_MAPPING, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise keyval.ObjectDNE(self)
            pipe.multi()
            pipe.hgetall(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return dict(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = dict(val)
        types = set([type(v) for v in val.values()])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in mapping".format(typ))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise keyval.ObjectExists(self)
            if not create and not exists:
                raise keyval.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.hmset(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableDictionary(MutableMapping, Dictionary, abc_base.MutableDictionary):

    pass
