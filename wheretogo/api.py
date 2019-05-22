"""
This module contains classes that allow to get free events from an api during a time period.

"""


class Api:
    def __init__(self, cache=None):
        self._cache = cache

    def get_events(self, date):
        raise NotImplementedError


class TicketmasterApi(Api):
    def __init__(self, query_params, cache=None):
        super().__init__(cache)
        self.query_params = query_params

    def get_events(self, date):
        raise NotImplementedError


class EventRange:
    def __init__(self, api):
        self._api = api

    def __call__(self, datetime_range, appointments):
        raise NotImplementedError
