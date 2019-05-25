[![Build Status](https://travis-ci.org/maqnius/wheretogo.svg?branch=master)](https://travis-ci.org/maqnius/wheretogo)

# WhereToGo?
WhereToGo is a simple example package, that allows to fetch event informations
from an api (ticketmaster.com api is given as example) and to process it further 
via filter functions. This way, one can for example filter the events by some 
given appointments.

## Installation
```python
python setup.py install
```

## Usage
A minimal example using the api from ticketmaster.com to print possible events in Berlin
that do not collide with appointments would look like this:
```python
from wheretogo.api import TicketmasterApi
from wheretogo.cache import DictionaryCache
from wheretogo.datefilter import TicketmasterAppointmentFilter

datetime_range = ('2019-05-25T00:00:00Z', '2019-05-26T00:00:00Z')
appointments = [('2019-05-25T12:00:00Z', '2019-05-25T14:00:00Z'), ('2019-05-25T19:00:00Z', '2019-05-25T21:00:00Z')]

# Create Api and define the used Caching method
api = TicketmasterApi(cache=DictionaryCache(), api_key="your_api_key")

# Initiate a filter
date_filter = TicketmasterAppointmentFilter(appointments)

# Fetch and filter events
events = api.get_events(datetime_range, date_filter=date_filter, city=["Berlin"])

# Print their names
for event in events:
    print(event["name"])

```
```
>>> 1. Boylesque Drag Festival Berlin
```

## Developer Interface
Install all necessary dependencies via

```python
pipenv install --dev
```

The main function that this packages provides to the outer world is `Api.get_events`, which
fetches and filters events.

The package provides necessary abstractions to be of general use whenever events are fetched from an api
and afterwards manipulated.

It mainly consists of three parts as can be seen in the minimal example.

#### Api Class `wheretogo.api.Api`
Subclass this abstract class to make an adapter to your api that holds event information.
At least the method `_request_get_events(start_date, end_date, *args, **kwargs)` needs to 
be filled with functionality. It returns all events in between `start_date` and `end_date`.

All parameters that are passed to `wheretogo.api.Api.get_events` (except `date_filter`) are
passed on to this function.

You maybe also want to overwrite the `_generate_cache_key(start_date, end_date, *args, **kwargs)` method
depending on your caching technique (see next class). It gets called to create the lookup key for the cache.

#### Cache Class `wheretogo.cache.Cache`
An abstract class that acts as an adapter to your caching implementation. It works
like a key-value storage. The methods for writing, reading and deleting data need to be implemented the
caching logic is abstracted in the `Cache` class.

Take a look at `wheretogo.api.Cache.DictionaryCache` as an example.

#### FilterFunction Class `wheretogo.datefilter.FilterFunction`
Implement this class by overwriting the `_filter` function in order to apply filter 
to the returns of your api. It's function `_filter` gets called on every event.

You can further use any other callable as a date_filter function.

### Tests
Tests are done using `pytest`.

You can run the tests via:

```python
python -m pytest tests/
```

