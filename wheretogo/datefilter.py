"""
This module contains valid filter functions for the :meth:`wheretogo.api.Api.get_events`
method.


"""
import datetime
import logging
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
        try:
            start_event = self._extract_time(event["dates"]["start"])
        except ValueError:
            return False

        try:
            end_event = self._extract_time(event["dates"]["end"])
        except ValueError:
            return False
        except KeyError:
            end_event = None

        for start_appointment, end_appointment in self.appointments:
            # Check if event is completely **after** appointment
            after = True
            if not start_event > end_appointment:
                after = False

            # Check if event is completely **before** appointment
            before = True
            if end_event is None or not end_event < start_appointment:
                before = False

            if not (after or before):     # Overlaps
                return True

        return False

    @staticmethod
    def _extract_time(event_date: dict) -> datetime.datetime:
        """
        Evaluates an Ticketmaster Event date field.
        If this is not possible, a ValueError is raised.

        :raises ValueError:

        TODO: Implement more possibilities of date extractions

        """
        try:
            return parse(event_date["dateTime"])
        except KeyError:
            logger.debug("Not dateTime field found.")
            pass

        logger.debug("Could not extract time from {}".format(event_date))
        raise ValueError  # Could not Extract
