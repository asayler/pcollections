# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Imports ###

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import native_str
from future.utils import viewitems
from builtins import *

import abc

from . import exceptions
from . import constants
from . import drivers
from . import abc_base


### Constants ###

_SEP_FIELD = ':'
_PREFIX_STRING = "string"
_PREFIX_LIST = "list"
_PREFIX_SET = "set"
_PREFIX_DICTIONARY = "hash"
_INDEX_KEY = "_obj_index"


### Base Objects ###

class Persistent(abc_base.Persistent):

    @abc.abstractmethod
    def __init__(self, driver, key, prefix, **kwargs):
        """ Constructor"""

        # Check Args
        if not isinstance(driver, drivers.RedisDriver):
            raise TypeError("driver must be instance of RedisDriver")

        # Save Extra Attrs
        self._redis_key = "{:s}{:s}{!s:s}".format(prefix, _SEP_FIELD, key)

        # Call Parent
        super(Persistent, self).__init__(driver, key, **kwargs)

    def _encode_val_item(self, item_in, test=False):
        """Encode single item as bytes"""

        item_out = item_in
        if isinstance(item_in, bytes):
            if not test:
                item_out = item_in
        elif isinstance(item_in, str) or isinstance(item_in, native_str):
            if not test:
                item_out = bytes(item_in.encode(constants.ENCODING))
        else:
            raise TypeError("Encoding type '{}' not supported".format(type(item_in)))
        return item_out

    def _decode_val_item(self, item_in, test=False):
        """Decode single item Python type"""

        item_out = item_in
        if isinstance(item_in, bytes):
            if not test:
                item_out = str(item_in.decode(constants.ENCODING))
        elif isinstance(item_in, str) or isinstance(item_in, native_str):
            if not test:
                item_out = item_in
        else:
            raise TypeError("Decoding '{}' not supported".format(type(item_in)))
        return item_out

    def _transact(self, func, *extra_watches, **kwargs):

        watches = [_INDEX_KEY, self._redis_key]
        watches += extra_watches
        return self.driver.redis.transaction(func, *watches, **kwargs)

    def _register(self, pipe):
        """Register Object as Existing"""

        pipe.sadd(_INDEX_KEY, self._redis_key)

    def _unregister(self, pipe):
        """Unregister Object as Existing"""

        pipe.srem(_INDEX_KEY, self._redis_key)

    def _exists_direct(self, pipe):
        """Check if Object Exists via pipe"""

        return bool(pipe.sismember(_INDEX_KEY, self._redis_key))

    def _init_val_raw(self, create=None, existing=None):

        # Check Args
        if existing is None or isinstance(existing, bool):
            pass
        else:
            raise TypeError("existing must be bool or None")

        # Init Transaction
        def atomic_init(pipe):

            exists = self._exists_direct(pipe)
            if exists:
                if existing is False:
                    # Fail - Exists
                    raise exceptions.ObjectExists(self)
                elif existing is True:
                    if create is not None:
                        # Overwrite
                        pipe.multi()
                        self._set_val_direct(pipe, create)
                    else:
                        # Open Existing
                        pass
                else:
                    # Open Existing
                    pass
            else:
                if existing is True:
                    # Fail - DNE
                    raise exceptions.ObjectDNE(self)
                else:
                    if create is not None:
                        # Create
                        pipe.multi()
                        self._register(pipe)
                        self._set_val_direct(pipe, create)
                    else:
                        # Open Nonexisting
                        pass

        # Execute Transaction
        self._transact(atomic_init)

    def _set_val_raw(self, val):

        # Set Transaction
        def atomic_set(pipe):

            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            self._set_val_direct(pipe, val)

        # Execute Transaction
        self._transact(atomic_set)

    @abc.abstractmethod
    def _set_val_direct(self, pipe, val):
        """Set value via pipe"""
        pass

    def _get_val_raw(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            self._get_val_direct(pipe)

        # Execute Transaction
        ret = self._transact(atomic_get)

        # Return Raw
        return ret[0]

    @abc.abstractmethod
    def _get_val_direct(self, pipe):
        """Get value via pipe"""
        pass

    def exists(self):
        """Check if Object Exists (Transaction)"""

        # Exists Transaction
        def atomic_exists(pipe):

            pipe.multi()
            self._exists_direct(pipe)

        # Check if Object Exists
        ret = self._transact(atomic_exists)

        # Return Bool
        return ret[0]

    def rem(self, force=False):
        """Delete Object"""

        # Delete Transaction
        def atomic_rem(pipe):

            if not self._exists_direct(pipe):
                if force:
                    return
                else:
                    raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.delete(self._redis_key)
            self._unregister(pipe)

        # Delete Object
        self._transact(atomic_rem)


### Objects ###

class String(Persistent, abc_base.String):

    def __init__(self, driver, key, **kwargs):
        """ Constructor"""

        # Call Parent
        super(String, self).__init__(driver, key, _PREFIX_STRING, **kwargs)

    def _map_conv_obj(self, obj_in, conv_func, test=False):
        return conv_func(obj_in, test=test)

    def _set_val_direct(self, pipe, val):

        pipe.set(self._redis_key, val)

    def _get_val_direct(self, pipe):

        pipe.get(self._redis_key)

class MutableString(String, abc_base.MutableString):
    pass

class List(Persistent, abc_base.List):

    def __init__(self, driver, key, **kwargs):
        """ Constructor"""

        # Call Parent
        super(List, self).__init__(driver, key, _PREFIX_LIST, **kwargs)

    def _map_conv_obj(self, obj_in, conv_func, test=False):

        obj_out = list()
        for item in obj_in:
            obj_out.append(conv_func(item, test=test))
        return obj_out

    def _set_val_direct(self, pipe, val):

        pipe.delete(self._redis_key)
        if len(val) > 0:
            pipe.rpush(self._redis_key, *val)

    def _get_val_direct(self, pipe):

        pipe.lrange(self._redis_key, 0, -1)

class MutableList(List, abc_base.MutableList):
    pass

class Set(Persistent, abc_base.Set):

    def __init__(self, driver, key, **kwargs):
        """Set Constructor"""

        # Call Parent
        super(Set, self).__init__(driver, key, _PREFIX_SET, **kwargs)

    def _map_conv_obj(self, obj_in, conv_func, test=False):

        obj_out = set()
        for item in obj_in:
            obj_out.add(conv_func(item, test=test))
        return obj_out

    def _set_val_direct(self, pipe, val):

        pipe.delete(self._redis_key)
        if len(val) > 0:
            pipe.sadd(self._redis_key, *val)

    def _get_val_direct(self, pipe):

        pipe.smembers(self._redis_key)

class MutableSet(Set, abc_base.MutableSet):
    pass

class Dictionary(Persistent, abc_base.Dictionary):

    def __init__(self, driver, key, **kwargs):
        """ Constructor"""

        # Call Parent
        super(Dictionary, self).__init__(driver, key, _PREFIX_DICTIONARY, **kwargs)

    def _map_conv_obj(self, obj_in, conv_func, test=False):

        obj_in = dict(obj_in)
        obj_out = dict()
        for key, val in viewitems(obj_in):
            key = conv_func(key, test=test)
            val = conv_func(val, test=test)
            obj_out[key] = val
        return obj_out

    def _set_val_direct(self, pipe, val):

        pipe.delete(self._redis_key)
        if len(val) > 0:
            pipe.hmset(self._redis_key, val)

    def _get_val_direct(self, pipe):

        pipe.hgetall(self._redis_key)

class MutableDictionary(Dictionary, abc_base.MutableDictionary):
    pass
