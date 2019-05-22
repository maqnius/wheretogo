"""
This module contains classes that allow to get free events from an api during a time period.

"""
import os
from requests import Request, Session


class Api:
    def __init__(self, cache=None):
        self._cache = cache

    def get_events(self, start_date, end_date):
        """
        Return list of Events during a period.

        :param datetime.datetime start_date: Only events after this date
        :param datetime.datetime end_date: Only events before this date
        :return: Events
        :rtype: list
        """
        raise NotImplementedError


class TicketmasterApi(Api):
    base_url = "https://app.ticketmaster.com/discovery/v2/"

    def __init__(self, api_key, query_params=None, cache=None):
        super().__init__(cache)
        self.api_key = api_key
        self.query_params = query_params or {}

    def get_events(self, start_date, end_date):
        params = self.query_params.copy()
        params["startDateTime"] = start_date.isoformat(timespec='seconds')
        params["endDateTime"] = end_date.isoformat(timespec='seconds')

        r = self._cached_request(
            rq_type='get',
            url=os.path.join(self.base_url, 'events.json'),
            params=self.query_params
        )

        return self._extract_names(r)

    @staticmethod
    def _extract_names(res) -> list:
        """
        Extracts event names from the json body of a Ticketmaster Api response

        :return: List of events
        :rtype: list
        """
        try:
            events = [event["name"] for event in res["_embedded"]["events"]]
        except KeyError:
            events = []

        return events

    @staticmethod
    def _eval_response(res) -> dict:
        """
        Evaluates a http response
        :raises HTTPError:

        """

        res.raise_for_status()
        return res.json()

    def _cached_request(self, rq_type, url, *args, **kwargs):
        """
        Prepares a request and executes only if request
        has not been cached yet.

        Passes any further parameters on to requests.Request class.

        :param str rq_type: 'POST', 'GET', etc.
        :param str url: Request url
        :return: Json-body of response if successfull else is raises a exception
        :raises HTTPError:

        """
        s = Session()

        # Prepare the request first to extract the whole query url
        # which is used as the key for the cache
        req = Request(rq_type, url, *args, **kwargs)
        prepped = req.prepare()

        if self._cache is None:  # Skip cache
            response = self._eval_response(s.send(prepped))
        else:
            # Use Cache if possible
            try:
                response = self._cache[prepped.path_url]
            except KeyError:
                response = self._eval_response(s.send(prepped))
                self._cache[prepped.path_url] = response

        return response


class EventRange:
    def __init__(self, api):
        self._api = api

    def __call__(self, datetime_range, appointments):
        raise NotImplementedError
