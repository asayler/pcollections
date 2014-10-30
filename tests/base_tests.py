# -*- coding: utf-8 -*-


# Andy Sayler
# Summer 2014
# Univerity of Colorado


### Imports ###

## stdlib ##
import copy
import unittest
import warnings

### keyval ###
import keyval.base


### Globals ###

_TEST_KEY_PRE = "TESTKEY"
_TEST_VAL_PRE_STRING = "TESTVAL"

### Initialization ###

warnings.simplefilter('default')


### Exceptions ###

class BaseTestError(Exception):
    """Base class for BaseTest Exceptions"""

    def __init__(self, *args, **kwargs):
        super(BaseTestError, self).__init__(*args, **kwargs)

### Base Class ###

class BaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.key_cnt = 0
        self.val_cnt = 0

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

    def generate_key(self):
        key = "{:s}_{:d}".format(_TEST_KEY_PRE, self.key_cnt)
        self.key_cnt += 1
        return key


### Base Mixins ###

class PersistentMixin(object):

    def __init__(self, *args, **kwargs):
        super(PersistentMixin, self).__init__(*args, **kwargs)

    def test_from_new(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.get_val())

        # Recreate New Instance
        self.assertRaises(keyval.base.ObjectExists, self.factory.from_new, key, val)

        # Cleanup
        instance.rem()

    def test_from_existing(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Get Nonexistant Instance
        self.assertRaises(keyval.base.ObjectDNE, self.factory.from_existing, key)

        # Create New Instance
        self.factory.from_new(key, val)

        # Get Existing Instance
        instance = self.factory.from_existing(key)
        self.assertTrue(instance)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.get_val())

        # Cleanup
        instance.rem()

    def test_from_raw(self):

        # Setup Test Vals
        key = self.generate_key()
        val = None

        # Get Raw Instance
        instance = self.factory.from_raw(key)
        self.assertFalse(instance)
        self.assertFalse(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertRaises(keyval.base.ObjectDNE, instance.get_val)

        # No Cleanup

    def test_rem(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())

        # Rem Instance
        instance.rem()
        self.assertFalse(instance.exists())

        # Rem Non-existant Instance (No Force)
        self.assertRaises(keyval.base.ObjectDNE, instance.rem)

        # Rem Non-existant Instance (Force)
        instance.rem(force=True)

        # No Cleanup

    def test_get_val(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())

        # Rem Instance
        instance.rem()
        self.assertRaises(keyval.base.ObjectDNE, instance.get_val)

        # No Cleanup

    def test_unicode(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(unicode(val), unicode(instance))

        # Cleanup
        instance.rem()

    def test_string(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(str(val), str(instance))

        # Cleanup
        instance.rem()

    def test_repr(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(key, repr(instance))

        # Cleanup
        instance.rem()

    def test_hash(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(hash(key), hash(instance))

        # Cleanup
        instance.rem()

    def test_bool(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance)

        # Cleanup
        instance.rem()

    def test_eq(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance_a = self.factory.from_new(key, val)
        instance_b = self.factory.from_existing(key)
        self.assertEqual(instance_a, instance_b)
        self.assertEqual(instance_b, instance_a)

        # Cleanup
        instance_b.rem()

    def test_ne(self):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        val = self.generate_val_multi()
        self.assertNotEqual(key_a, key_b)

        # Create Instance
        instance_a = self.factory.from_new(key_a, val)
        instance_b = self.factory.from_new(key_b, val)
        self.assertNotEqual(val, instance_a)
        self.assertNotEqual(instance_a, val)
        self.assertNotEqual(val, instance_b)
        self.assertNotEqual(instance_b, val)
        self.assertNotEqual(instance_a, instance_b)

        # Cleanup
        instance_a.rem()
        instance_b.rem()

class MutableMixin(PersistentMixin):

    def __init__(self, *args, **kwargs):
        super(MutableMixin, self).__init__(*args, **kwargs)

    def test_set_val(self):

        # Setup Test Vals
        key = self.generate_key()
        val1 = self.generate_val_multi()
        val2 = self.generate_val_multi()
        val3 = self.generate_val_multi()

        # Create New Instance and Set Value
        instance = self.factory.from_new(key, val1)
        instance.set_val(val2)
        self.assertEqual(val2, instance.get_val())

        # Rem Instance
        instance.rem()
        self.assertRaises(keyval.base.ObjectDNE, instance.set_val, val3)

        # No Cleanup

class SequenceMixin(PersistentMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)

    def test_len(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(len(val), len(instance))

        # Rem Instance
        instance.rem()
        self.assertRaises(keyval.base.ObjectDNE, len, instance)

        # No Cleanup

    def test_getitem(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)
        for i in range(len(val)):
            self.assertEqual(val[i], instance[i])

        # Cleanup
        instance.rem()

    def test_contains(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)
        for i in val:
            self.assertTrue(i in instance)
        self.assertFalse(self.generate_val_multi() in instance)

        # Cleanup
        instance.rem()

    def test_iter(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        cnt = 0
        for i in instance:
            self.assertEqual(val[cnt], i)
            cnt += 1

        # Cleanup
        instance.rem()

    def test_reversed(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        cnt = -1
        for i in reversed(instance):
            self.assertEqual(val[cnt], i)
            cnt -= 1

        # Cleanup
        instance.rem()

    def test_index(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        for i in val:
            self.assertEqual(val.index(i), instance.index(i))

        # Cleanup
        instance.rem()

    def test_count(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi()

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        for i in val:
            self.assertEqual(val.count(i), instance.count(i))

        # Cleanup
        instance.rem()

class MutableSequenceMixin(SequenceMixin, MutableMixin):

    def __init__(self, *args, **kwargs):
        super(MutableSequenceMixin, self).__init__(*args, **kwargs)

    def test_setitem(self):

        def setitem(instance, i, v):
            x = instance[i] = v
            return x

        def setitem_test_good(i, l):
            key = self.generate_key()
            val = self.generate_val_multi(length=l)
            new = self.generate_val_multi(length=0)
            v = self.generate_val_single()
            instance = self.factory.from_new(key, val)
            self.assertEqual(val, instance.get_val())
            self.assertEqual(v, setitem(instance, i, v))
            if (i != 0) and (i != -l):
                new += val[:i]
            new += v
            if (i != (l-1)) and (i != -1):
                new += val[i+1:]
            self.assertNotEqual(new, val)
            self.assertEqual(len(new), len(val))
            self.assertEqual(new, instance.get_val())
            instance.rem()

        def setitem_test_null(i):
            key = self.generate_key()
            v = self.generate_val_single()
            instance = self.factory.from_raw(key)
            self.assertFalse(instance.exists())
            self.assertRaises(keyval.base.ObjectDNE, setitem, instance, i, v)

        def setitem_test_oob(i, l):
            key = self.generate_key()
            val = self.generate_val_multi(length=l)
            v = self.generate_val_single()
            instance = self.factory.from_new(key, val)
            self.assertEqual(val, instance.get_val())
            self.assertRaises(IndexError, setitem, instance, i, v)
            instance.rem()

        def setitem_test_badval(i, l):
            key = self.generate_key()
            val = self.generate_val_multi(length=l)
            v = self.generate_val_multi(3)
            instance = self.factory.from_new(key, val)
            self.assertEqual(val, instance.get_val())
            self.assertRaises(ValueError, setitem, instance, i, v)
            instance.rem()

        # Test Null Instance
        setitem_test_null( 0)
        setitem_test_null(-1)
        setitem_test_null( 1)

        # Test Empty Instance
        setitem_test_oob( 0, 0)
        setitem_test_oob( 1, 0)
        setitem_test_oob(-1, 0)

        # Test Valid
        setitem_test_good(  0, 10)
        setitem_test_good(-10, 10)
        setitem_test_good(  5, 10)
        setitem_test_good( -5, 10)
        setitem_test_good(  9, 10)
        setitem_test_good( -1, 10)

        # Test OOB
        setitem_test_oob( 10, 10)
        setitem_test_oob( 11, 10)
        setitem_test_oob(-11, 10)
        setitem_test_oob(-12, 10)

        # Test Bad Val
        setitem_test_badval(  0, 10)
        setitem_test_badval(-10, 10)
        setitem_test_badval(  5, 10)
        setitem_test_badval( -5, 10)
        setitem_test_badval(  9, 10)
        setitem_test_badval( -1, 10)

    def test_delitem(self):

        def delitem(instance, i):
            del(instance[i])

        def delitem_test_good(i, l):
            key = self.generate_key()
            val = self.generate_val_multi(length=l)
            new = self.generate_val_multi(length=0)
            instance = self.factory.from_new(key, val)
            self.assertEqual(val, instance.get_val())
            delitem(instance, i)
            if (i != 0) and (i != -l):
                new += val[:i]
            if (i != (l-1)) and (i != -1):
                new += val[i+1:]
            self.assertNotEqual(new, val)
            self.assertEqual(new, instance.get_val())
            instance.rem()

        def delitem_test_null(i):
            key = self.generate_key()
            instance = self.factory.from_raw(key)
            self.assertFalse(instance.exists())
            self.assertRaises(keyval.base.ObjectDNE, delitem, instance, i)

        def delitem_test_oob(i, l):
            key = self.generate_key()
            val = self.generate_val_multi(length=l)
            instance = self.factory.from_new(key, val)
            self.assertEqual(val, instance.get_val())
            self.assertRaises(IndexError, delitem, instance, i)
            instance.rem()

        # Test Null Instance
        delitem_test_null( 0)
        delitem_test_null(-1)
        delitem_test_null( 1)

        # Test Empty Instance
        delitem_test_oob( 0, 0)
        delitem_test_oob( 1, 0)
        delitem_test_oob(-1, 0)

        # Test Valid
        delitem_test_good(  0, 10)
        delitem_test_good(-10, 10)
        delitem_test_good(  5, 10)
        delitem_test_good( -5, 10)
        delitem_test_good(  9, 10)
        delitem_test_good( -1, 10)

        # Test OOB
        delitem_test_oob( 10, 10)
        delitem_test_oob( 11, 10)
        delitem_test_oob(-11, 10)
        delitem_test_oob(-12, 10)

    def helper_test_wrapper(self, size, test_func, index, item, ref_func):

        key = self.generate_key()
        old = self.generate_val_multi(length=size)
        instance = self.factory.from_new(key, old)
        self.assertEqual(old, instance.get_val())
        test_func(instance, index, item)
        new = ref_func(old, index, item)
        self.assertNotEqual(old, new)
        self.assertEqual(new, instance.get_val())
        instance.rem()

    def helper_test_raises(self, size, test_func, index, item, error):

        key = self.generate_key()
        val = self.generate_val_multi(length=size)
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())
        self.assertRaises(error, test_func, instance, index, item)
        instance.rem()

    def helper_test_dne(self, test_func, index, item):
        key = self.generate_key()
        instance = self.factory.from_raw(key)
        self.assertFalse(instance.exists())
        self.assertRaises(keyval.base.ObjectDNE, test_func, instance, index, item)

    def test_insert(self):

        def test_func(instance, index, item):
            return instance.insert(index, item)

        def ref_func(ref, index, item):
            return ref[:index] + item + ref[index:]

        def insert_test_good(index, size):
            item = self.generate_val_multi(length=1)
            self.helper_test_wrapper(size, test_func, index, item, ref_func)

        def insert_test_badval(index, size):
            item = self.generate_val_multi(length=3)
            self.helper_test_raises(size, test_func, index, item, ValueError)

        def insert_test_null(index):
            item = self.generate_val_multi(length=1)
            self.helper_test_dne(test_func, index, item)

        # test Null Instance
        insert_test_null( 0)
        insert_test_null( 1)
        insert_test_null(-1)

        # Test Bad Val
        insert_test_badval(  0, 10)
        insert_test_badval(-10, 10)
        insert_test_badval(  5, 10)
        insert_test_badval( -5, 10)
        insert_test_badval(  9, 10)
        insert_test_badval( -1, 10)

        # Test Empty Instance
        insert_test_good( 0, 0)
        insert_test_good( 1, 0)
        insert_test_good(-1, 0)

        # Test Insert Before
        insert_test_good(-12, 10)
        insert_test_good(-11, 10)

        # Test Insert Beginning
        insert_test_good(  0, 10)
        insert_test_good(-10, 10)

        # Test Instance - Middle
        insert_test_good( 5, 10)
        insert_test_good(-5, 10)

        # Test Insert End
        insert_test_good( 9, 10)
        insert_test_good(-1, 10)

        # Test Instert After
        insert_test_good(10, 10)
        insert_test_good(11, 10)


### Object Mixins ###

class StringMixin(SequenceMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.String)

    def generate_val_single(self):

        cnt = self.val_cnt % 26
        self.val_cnt += 1
        return chr(ord('A') + cnt)

    def generate_val_multi(self, length=10):

        val = ""
        for i in range(length):
            val += self.generate_val_single()
        return val

class MutableStringMixin(MutableSequenceMixin, StringMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.MutableString)
