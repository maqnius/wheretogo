class AppointmentFilter:
    """
    Filters events by checking if they overlap
    with any appointment.

    """
    def __init__(self, appointments):
        """

        :param list appointments: List of appointments given as a tuple (start-date, end-date)
            where each of those dates are either a valid date sting or a python
            :class:`datetime.datetime` object.

        """
        self.appointments = appointments

    def __call__(self, events, *args, **kwargs):
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
                        "localDate": "2016-03-06",
                        "dateTBD": false,
                        "dateTBA": false,
                        "timeTBA": true,
                        "noSpecificTime": false
                    }

        :return list filtered_events: List of all events that do not overlap
            with any appointment.

        """
        return events
