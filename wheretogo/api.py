"""
This module contains classes that allow to get free events from an api during a time period.

"""
import logging
import os
from dateutil.parser import parse
import requests

logger = logging.getLogger(__name__)


class Api:
    def __init__(self, cache=None):
        self._cache = cache

    def get_events(self, date_range, date_filter=None, *args, **kwargs):
        """
        Return list of Events during a period using cached requests

        :param date_range: Only events after this date
        :type date_range: (str|datetime.datetime, str|datetime.datetime)
        :param date_filter: List of filter functions or a single filter function that are applied on the query result
        :type date_filter: [callable] or callable
        :return: Events
        :rtype: list
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
                logger.debug("Making a request because cache does not hold request data")
                events = self._request_get_events(start_date, end_date, *args, **kwargs)
                self._cache[key] = events

        return self._apply_filter(events, date_filter, *args, **kwargs)

    @staticmethod
    def _apply_filter(events, date_filter, *args, **kwargs):
        for f in date_filter:
            events = f(events, *args, **kwargs)

        return events

    @staticmethod
    def _generate_cache_key(start_date, end_date, *args, **kwargs):
        params = ["{}={}".format(name, value) for name, value in kwargs.items()]
        return (start_date, end_date, *args, *params)

    def _request_get_events(self, start_date, end_date, *args, **kwargs):
        raise NotImplementedError


class TicketmasterApi(Api):
    base_url = "https://app.ticketmaster.com/discovery/v2/"

    def __init__(self, api_key, cache=None):
        super().__init__(cache)
        self.api_key = api_key

    def _request_get_events(self, start_date, end_date, *args, **kwargs):
        params = kwargs
        params["apikey"] = self.api_key

        r = requests.get(os.path.join(self.base_url, 'events.json'), params=params)
        r.raise_for_status()
        r = r.json()

        return self._extract_names(r)

    @staticmethod
    def _extract_names(res) -> list:
        """
        Extracts event names from the json body of a Ticketmaster Api response

        :return: List of events
        :rtype: list
        """
        try:
            return res["_embedded"]["events"]
        except KeyError:
            return []
