"""
This module contains cache objects that can be used by the api classes
defined in :mod:`wheretogo.api` to cache api requests.

"""
import time
from abc import ABC, abstractmethod


class Cache(ABC):
    """
    Represents a simple cache class.

    To the outside world, it behaves like a simple key-value-store.
    Internally it also manages a timeout if given.

    Implementations of this class must implement the :meth:`_del`, :meth:`_load`
    and :meth:`_save` method.

    """

    def __init__(self, timeout=None):
        """
        :param int timeout: Timespan in seconds for which a cache entry is valid

        """
        self.timeout = timeout

    def __getitem__(self, item):
        """
        Returns a cached value if it is in the cache
        and not older as :attr:`self.timeout`.

        If the value is not in the cache, it raises
        a KeyError.

        :raise KeyError:
        :param item: Lookup key for the cache
        :return: Cached value if it does exist
        """
        try:
            value, timestamp = self._get(item)
        except KeyError:
            raise
        else:
            if self.timeout is None or time.time() - timestamp < self.timeout:
                return value
            else:
                self._del(item)
                raise KeyError()

    def __setitem__(self, key, value) -> None:
        self._set(key, value, time.time())

    @abstractmethod
    def _del(self, item) -> None:
        """
        Deletion of an item

        :param item: key
        :return: None
        """
        pass

    @abstractmethod
    def _get(self, item):
        """
        Get a value and timestamp. If the item is not stored in the cache,
        a KeyError must be raised.

        :raises KeyError:
        :param item: The cache key
        :return: Tuple (value, timestamp) containing the cached value or the timestapm
        :rtype: (value, POSIX timestamp)
        """
        pass

    @abstractmethod
    def _set(self, item, value, timestamp):
        """
        Saves a item-value pair into the cache as well as the timestamp when
        this did happen.

        :param item: The lookup key
        :param value: Value to be cached
        :param timestamp: POSIX-Timestamp when the value has been saved to cached
        """
        pass


class DictionaryCache(Cache):
    """
    Implementation of :class:`Cache`.

    Uses a python dictionary as storage.

    """

    def __init__(self, timeout=None):
        super().__init__(timeout)
        self._cache = {}

    def _get(self, item):
        return self._cache[item]

    def _set(self, item, value, timestamp) -> None:
        self._cache[item] = (value, timestamp)

    def _del(self, item) -> None:
        del self._cache[item]
