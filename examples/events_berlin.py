"""
This is an example how to get all events in berlin during a timespan
and exclude events during an appointment
"""
from wheretogo.api import TicketmasterApi
from wheretogo.cache import DictionaryCache
from wheretogo.datefilter import TicketmasterAppointmentFilter

api = TicketmasterApi(cache=DictionaryCache(), api_key="your_api_key")


def events_in_berlin(date_range, appointments):
    """Prints names of all events during a date range that do not conflict with appointments"""
    date_filter = TicketmasterAppointmentFilter(appointments)

    events = api.get_events(date_range, date_filter=date_filter, city=["Berlin"])

    for event in events:
        print(event["name"])


datetime_range = ('2019-05-22T00:00:00Z', '2019-05-23T00:00:00Z')
appointments = [('2019-05-16T12:00:00Z', '2019-05-16T14:00:00Z'), ('2019-05-17T19:00:00Z', '2019-05-17T21:00:00Z')]

events_in_berlin(datetime_range, appointments)
