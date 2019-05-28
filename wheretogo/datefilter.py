"""
This module contains valid filter functions for the :meth:`wheretogo.api.Api.get_events`
method.


"""
import datetime
import logging
import pytz
from typing import Tuple, List
from abc import ABC, abstractmethod
from dateutil.parser import parse
from .utils import eventType, datesType

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FilterFunction(ABC):
    """FilterFunction base class"""

    def __call__(self, events: List[eventType], *args, **kwargs) -> List[eventType]:
        return [e for e in events if self._filter(e)]

    @abstractmethod
    def _filter(self, event: eventType) -> bool:
        """
        :param event:
        :return: True if event gets past the filter, False else
        """


class TicketmasterAppointmentFilter(FilterFunction):
    """
    Example filter function

    Filters events by checking if they overlap
    with any appointment.

    """

    def __init__(self, appointments: List[Tuple[datesType, datesType]]):
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

    def _filter(self, event: eventType) -> bool:
        """
        Checks if a single event does not overlap with any of the appointments

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

        :returns: True if it does not overlap, False else
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
                return False

        return True

    def _extract_date_rage(
        self, event_date: eventType
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """Creates a (start_date, end_date) tuple from the event's date information"""
        start_event = self._extract_date(
            event_date["start"], event_date.get("timezone", "")
        )

        try:
            end_event = self._extract_date(
                event_date["end"], event_date.get("timezone", "")
            )
        except KeyError:
            end_event = None

        return start_event, end_event

    @staticmethod
    def _extract_date(event_date: eventType, timezone: str) -> datetime.datetime:
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

        raise ValueError(
            "Could not extract time from {}".format(event_date)
        )  # Could not Extract
