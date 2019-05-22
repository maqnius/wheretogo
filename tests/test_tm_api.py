import requests
import os
from tests.config import API_KEY

ROOT_URL = "https://app.ticketmaster.com/discovery/v2/"


def test_api_key():
    """
    Test via example from the ticketmaster tutorial.
    """
    url = os.path.join(
        ROOT_URL, "events.json?countryCode=US&apikey={}".format(API_KEY)
    )

    foo = requests.get(url)

    assert foo.status_code == requests.codes.ok
