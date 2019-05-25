import requests
import pytest
import os
import datetime
from tests.config import API_KEY
from wheretogo.api import TicketmasterApi
from wheretogo.datefilter import TicketmasterAppointmentFilter
from wheretogo.cache import DictionaryCache

if "apikey" in os.environ:
    API_KEY = os.environ["apikey"]

ROOT_URL = "https://app.ticketmaster.com/discovery/v2/"
today = datetime.datetime.today()
tomorrow = today + datetime.timedelta(days=1)
yesterday = today - datetime.timedelta(days=1)

datetime_range = (today.isoformat(timespec="seconds") + "Z", tomorrow.isoformat(timespec="seconds") + "Z")
invalid_datetime_range = (yesterday.isoformat(timespec="seconds") + "Z", today.isoformat(timespec="seconds") + "Z")
appointments = [('2019-05-22T12:00:00Z', '2019-05-22T14:00:00Z'), ('2019-05-22T19:00:00Z', '2019-05-22T21:00:00Z')]
query_params = {"city": ["Berlin"], "apikey": API_KEY}


@pytest.fixture
def api():
    api = TicketmasterApi(api_key=API_KEY)
    return api


@pytest.fixture
def cached_api():
    api = TicketmasterApi(api_key=API_KEY, cache=DictionaryCache())
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

    events = api.get_events(datetime_range, city=query_params["city"])

    assert type(events) == list
    assert len(events) > 0

    events = api.get_events(invalid_datetime_range, city=query_params["city"])

    assert len(events) == 0


def test_get_event_range(cached_api):
    """
    Test if filtering of the events works
    """
    # make appointment over whole timespan
    long_appointment = TicketmasterAppointmentFilter([datetime_range])
    filtered_events = cached_api.get_events(datetime_range, date_filter=long_appointment, city=query_params["city"])

    assert len(filtered_events) == 0

    appointment_filter = TicketmasterAppointmentFilter(appointments)

    filtered_events = cached_api.get_events(datetime_range, date_filter=appointment_filter, city=query_params["city"])

    assert type(filtered_events) == list

    events = cached_api.get_events(datetime_range, city=query_params["city"])

    assert len(events) >= len(filtered_events)
