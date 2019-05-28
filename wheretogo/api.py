"""
This module contains classes that allow to get free events from an api during a time period.

"""
import logging
import os
import datetime
import requests
from typing import Tuple, Callable, Union, List, Any
from abc import ABC, abstractmethod
from dateutil.parser import parse
from .cache import Cache, itemType
from .utils import datesType, eventType

logger = logging.getLogger(__name__)

filterType = Union[Callable, List[Callable]]
datetimeType = datetime.datetime


class Api(ABC):
    """
    Abstract class for getting events during in a specific date range
    from *some external source* (cached) and filtering them.

    .. important::
        All implementation of these must overwrite the :meth:`._request_get_events`
        method which does the actual data fetch from the external source.

    """

    def __init__(self, cache: Cache = None):
        self._cache = cache

    def get_events(
        self,
        date_range: Tuple[datesType, datesType],
        date_filter: filterType = None,
        *args,
        **kwargs
    ) -> List[eventType]:
        """
        Return list of Events during a period using cached requests

        :param date_range: Only events after this date
        :param date_filter: List of filter functions or a single filter function that are applied on the query result
        :return: Events
        """
        date_filter = date_filter or []
        if type(date_filter) is not list:
            date_filter = [date_filter]

        start_date, end_date = date_range

        if type(start_date) == str:
            start_date = parse(start_date)

        if type(end_date) == str:
            end_date = parse(end_date)

        key = self._generate_cache_key(start_date, end_date, *args, **kwargs)

        if self._cache is None:
            logger.debug("Making a request because no cache is set")
            events = self._request_get_events(start_date, end_date, *args, **kwargs)
        else:
            try:
                events = self._cache[key]
                logger.debug("Got events from cache")
            except KeyError:
                logger.debug(
                    "Making a request because cache does not hold request data"
                )
                events = self._request_get_events(start_date, end_date, *args, **kwargs)
                self._cache[key] = events

        return self._apply_filter(events, date_filter, *args, **kwargs)

    @staticmethod
    def _apply_filter(
        events: List[eventType], date_filter: filterType, *args, **kwargs
    ) -> List[eventType]:
        for f in date_filter:
            events = f(events, *args, **kwargs)

        return events

    @staticmethod
    def _generate_cache_key(
        start_date: datetimeType, end_date: datetimeType, *args, **kwargs
    ) -> itemType:
        params = ["{}={}".format(name, value) for name, value in kwargs.items()]
        return (start_date.isoformat(), end_date.isoformat(), *args, *params)

    @abstractmethod
    def _request_get_events(
        self, start_date: datetimeType, end_date: datetimeType, *args, **kwargs
    ) -> List[eventType]:
        """
        This method needs to filled with live by all implementations of this Api.

        It gets called whenever a list of events in a time-period defined by
        start_date and end_date is not found in the cache.

        What it returns depends on how you want to use the data later and is
        for example restricted by the filter functions (see :mod:`wheretogo.datefilter`that might be applied
        on them.)

        .. important::
            It gets called with all the parameters that the public function :meth:`.get_events` got called.

        :param start_date: All Events must happen past this date
        :param end_date:  All Events must happen before this date
        :return:
        """


class TicketmasterApi(Api):
    """
    This accesses the ticketmaster.com api to fetch events

    """

    base_url = "https://app.ticketmaster.com/discovery/v2/"

    def __init__(self, api_key: str, cache: Cache = None):
        super().__init__(cache)
        self.api_key = api_key

    def _request_get_events(
        self, start_date: datetimeType, end_date: datetimeType, *args, **kwargs
    ):
        """
        See :meth:`.api._requests_get_events`.

        TODO: Result is paginated. Fetch information of all pages.

        """
        params = kwargs
        params["apikey"] = self.api_key
        params["startDateTime"] = start_date.isoformat(timespec="seconds")
        params["endDateTime"] = end_date.isoformat(timespec="seconds")

        r = requests.get(os.path.join(self.base_url, "events.json"), params=params)
        r.raise_for_status()
        r = r.json()

        return self._extract_names(r)

    @staticmethod
    def _extract_names(res: dict) -> list:
        """
        Extracts event names from the json body of a Ticketmaster Api response

        :return: List of events
        """
        try:
            return res["_embedded"]["events"]
        except KeyError:
            return []
