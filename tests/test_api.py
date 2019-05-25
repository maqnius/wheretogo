import pytest
from wheretogo.api import Api


def test_class():
    """Test abstract class"""
    with pytest.raises(TypeError):
        api = Api()
