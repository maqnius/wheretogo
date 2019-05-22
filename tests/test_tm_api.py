import requests
import pytest
import os
from dateutil.parser import parse
from tests.config import API_KEY
from wheretogo.api import TicketmasterApi, EventRange

ROOT_URL = "https://app.ticketmaster.com/discovery/v2/"

datetime_range = ('2019-05-22T00:00:00Z', '2019-05-23T00:00:00Z')
appointments = [('2019-05-16T12:00:00Z', '2019-05-16T14:00:00Z'), ('2019-05-17T19:00:00Z', '2019-05-17T21:00:00Z')]
query_params = {"city": ["Berlin"], "apikey": API_KEY}


@pytest.fixture
def api():
    api = TicketmasterApi(query_params)
    return api


def test_api_key():
    """
    Test via example from the ticketmaster tutorial.
    """
    url = os.path.join(
        ROOT_URL, "events.json"
    )

    foo = requests.get(url, params=query_params)

    assert foo.status_code == requests.codes.ok


def test_get_events(api):
    """
    Check if api calls basically work.

    There is no more advanced testing since
    it would mean reproducing the code of the module.

    """
    start_date = parse(datetime_range[0])
    end_date = parse(datetime_range[1])

    events = api.get_events((start_date, end_date))

    assert type(events) == list


def test_get_event_range(api):
    """
    Test if filtering of the events works
    """
    wtgo = EventRange(api=api)
    event_range = wtgo(datetime_range, appointments)

    assert type(event_range) == list

    start_date = parse(datetime_range[0])
    end_date = parse(datetime_range[1])

    events = api.get_events((start_date, end_date))

    assert len(events) >= len(event_range)
