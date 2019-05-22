import pytest
import time
from time import sleep
from wheretogo.cache import SimpleCache


def test_cache_w_timeout():
    """
    Test creation of values and
    if timout makes the content invalid
    """
    w_timeout = SimpleCache(timeout=1)
    w_timeout["foo"] = "bar"

    assert w_timeout["foo"] == "bar"

    sleep(2)

    with pytest.raises(KeyError):
        bar = w_timeout["foo"]

    assert "foo" not in w_timeout._cache


def test_cache_without_timeout():
    """
    Test creation of values and
    if timout makes the content invalid
    """
    w_timeout = SimpleCache()
    w_timeout["foo"] = "bar"

    assert w_timeout["foo"] == "bar"

    value, timestamp = w_timeout._cache["foo"]

    assert timestamp < time.time()
