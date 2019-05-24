import pytest
from wheretogo.api import Api


def test_class():
    """Test abstract class"""
    api = Api()

    with pytest.raises(NotImplementedError):
        api._request_get_events(None, None, None)
