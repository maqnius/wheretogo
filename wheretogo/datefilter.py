"""
This module contains valid filter functions for the :meth:`wheretogo.api.Api.get_events`
method.


"""
import datetime
import logging
import pytz
from dateutil.parser import parse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FilterFunction:
    """FilterFunction base class"""

    def __call__(self, events: [dict], *args, **kwargs) -> [dict]:
        raise NotImplementedError


class TicketmasterAppointmentFilter(FilterFunction):
    """
    Example filter function

    Filters events by checking if they overlap
    with any appointment.

    """

    def __init__(self, appointments: [tuple]):
        """

        :param appointments: List of appointments given as a tuple (start-date, end-date)
            where each of those dates are either a valid date sting or a python
            :class:`datetime.datetime` object.

        """
        self.appointments = []

        for start, end in appointments:
            if type(start) == str:
                start = parse(start)
            if type(end) == str:
                end = parse(end)

            self.appointments.append((start, end))

    def __call__(self, events: [dict], *args, **kwargs) -> [dict]:
        """

        :param list events: List of dictionaries. Each dictionary represents an
            Event and contains at least the following fields:

            :name:
                The events name
            :dates:
                A dictionary containing start information according to this
                scheme:

                .. code-block::javascript

                    "start":  {
                        "dateTime": "2019-11-01T17:30:00Z",
                        ...
                    },
                    "end":  {
                        "dateTime": "2019-11-01T18:30:00Z",
                        ...
                    }

        :return list filtered_events: List of all events that do not overlap
            with any appointment.

        """
        return [e for e in events if not self._overlaps(e)]

    def _overlaps(self, event: dict) -> bool:
        """
        Checks if a single event overlaps with any of the appointments

        :param event: See `:meth:.__call__`

        """
        start_event, end_event = self._extract_date_rage(event["dates"])

        for start_appointment, end_appointment in self.appointments:
            # Check if event is completely **after** appointment
            after = True
            if not start_event > end_appointment:
                after = False

            # Check if event is completely **before** appointment
            before = True
            if end_event is None or not end_event < start_appointment:
                before = False

            if not (after or before):  # Overlaps
                return True

        return False

    def _extract_date_rage(self, event_date: dict) -> (datetime.datetime, datetime.datetime):
        start_event = self._extract_date(event_date["start"], event_date.get("timezone", ""))
        try:
            end_event = self._extract_date(event_date["end"], event_date.get("timezone", ""))
        except KeyError:
            end_event = None

        return start_event, end_event

    @staticmethod
    def _extract_date(event_date: dict, timezone: str) -> datetime.datetime:
        """
        Evaluates an Ticketmaster Event date field.
        If this is not possible, a ValueError is raised.

        :raises ValueError:

        TODO: Implement more possibilities of date extractions

        """
        # Look for iso timestamp
        try:
            return parse(event_date["dateTime"])
        except KeyError:
            logger.debug("Not dateTime field found.")
            pass

        # Try with local time
        try:
            date = parse(event_date["localDate"])
        except KeyError:
            logger.debug("Not localDate field found.")
            pass
        else:
            try:
                return date.replace(tzinfo=pytz.timezone(timezone))
            except pytz.UnknownTimeZoneError:
                pass

        raise ValueError("Could not extract time from {}".format(event_date))  # Could not Extract
