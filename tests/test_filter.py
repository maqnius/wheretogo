from wheretogo.datefilter import TicketmasterAppointmentFilter

appointments = [('2019-05-16T12:00:00Z', '2019-05-16T14:00:00Z'), ('2019-05-17T19:00:00Z', '2019-05-17T21:00:00Z')]

test_events = [
    {
        "name": "EventA",  # Conflicts with first appointment (ends too late)
        "dates": {
            "start": {
                "dateTime": "2019-05-16T11:30:00Z",
            },
            "end": {
                "dateTime": "2019-05-16T13:30:00Z",
            }
        }

    },
    {
        "name": "EventB",  # Conflicts with first appointment (starts too early)
        "dates": {
            "start": {
                "dateTime": "2019-05-16T13:00:00Z",
            },
            "end": {
                "dateTime": "2019-05-16T14:30:00Z",
            }
        }

    },
    {
        "name": "EventC",  # No conflict
        "dates": {
            "start": {
                "dateTime": "2019-05-16T14:10:00Z",
            },
            "end": {
                "dateTime": "2019-05-16T14:30:00Z",
            }
        }

    },
    {
        "name": "EventD",  # Conflicts with last appointment
        "dates": {
            "start": {
                "dateTime": "2019-05-17T19:30:00Z",
            },
            "end": {
                "dateTime": "2019-05-17T20:00:00Z",
            }
        }

    }
]


def test_appointment_filter():
    appointment_filter = TicketmasterAppointmentFilter(appointments)

    filtered_events = appointment_filter(test_events)

    assert len(filtered_events) == 1
    assert filtered_events[0]["name"] == "EventC"
