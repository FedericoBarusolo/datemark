import pytest
from datetime import datetime as dt
from models.io_models import Event, EventList


@pytest.mark.unit
@pytest.mark.parametrize("event,output",
                         [(Event(title="KK Concert",
                                 start_time=dt.strptime("2025-01-01T21.00", "%Y-%m-%dT%H.%M"),
                                 end_time=dt.strptime("2025-01-01T23.00", "%Y-%m-%dT%H.%M"),
                                 location="Crossing Island",
                                 time_zone="Europe/London"),
                           "Title: KK Concert"
                           "\nStart Time: 2025-01-01 21:00:00"
                           "\nEnd Time: 2025-01-01 23:00:00"
                           "\nLocation: Crossing Island\n"),

                          (Event(title="KK Concert",
                                 start_time=dt.strptime("2025-01-01T21.00", "%Y-%m-%dT%H.%M"),
                                 location="Crossing Island",
                                 time_zone="Europe/London"),
                           "Title: KK Concert"
                           "\nStart Time: 2025-01-01 21:00:00"
                           "\nEnd Time: None"
                           "\nLocation: Crossing Island\n")])
def test_event_str(event, output):
    assert str(event) == output


@pytest.mark.unit
@pytest.mark.parametrize("event_list,output",
                         [(EventList(events=[
                             Event(title="KK Concert",
                                   start_time=dt.strptime("2025-01-01T21.00", "%Y-%m-%dT%H.%M"),
                                   end_time=dt.strptime("2025-01-01T23.00", "%Y-%m-%dT%H.%M"),
                                   location="Crossing Island",
                                   time_zone="Europe/London"),
                         ]),
                           "Title: KK Concert"
                           "\nStart Time: 2025-01-01 21:00:00"
                           "\nEnd Time: 2025-01-01 23:00:00"
                           "\nLocation: Crossing Island\n"
                           + "-" * 20 + "\n")
                         ])
def test_eventlist_str(event_list, output):
    assert str(event_list) == output


@pytest.mark.unit
@pytest.mark.parametrize("event,output",
                         [(Event(title="KK Concert",
                                 start_time=dt.strptime("2025-01-01T21.00", "%Y-%m-%dT%H.%M"),
                                 end_time=dt.strptime("2025-01-01T23.00", "%Y-%m-%dT%H.%M"),
                                 location="Crossing Island",
                                 time_zone="Europe/London"),
                           {"title": "KK Concert",
                            "start_time": "2025-01-01T21:00:00",
                            "end_time": "2025-01-01T23:00:00",
                            "location": "Crossing Island",
                            "time_zone": "Europe/London",
                            "day_of_week": "Wednesday"}),

                          (Event(title="KK Concert",
                                 start_time=dt.strptime("2025-01-01T21.00", "%Y-%m-%dT%H.%M"),
                                 location="Crossing Island",
                                 time_zone="Europe/London"),
                           {"title": "KK Concert",
                            "start_time": "2025-01-01T21:00:00",
                            "end_time": None,
                            "location": "Crossing Island",
                            "time_zone": "Europe/London",
                            "day_of_week": "Wednesday"})])
def test_event_dump(event, output):
    assert event.model_dump() == output


@pytest.mark.unit
@pytest.mark.parametrize("event_list,output",
                         [(EventList(events=
                                     [Event(title="KK Concert",
                                            start_time=dt.strptime("2025-01-01T21.00", "%Y-%m-%dT%H.%M"),
                                            end_time=dt.strptime("2025-01-01T23.00", "%Y-%m-%dT%H.%M"),
                                            location="Crossing Island",
                                            time_zone="Europe/London")]),
                           {"events":
                                [{"title": "KK Concert",
                                  "start_time": "2025-01-01T21:00:00",
                                  "end_time": "2025-01-01T23:00:00",
                                  "location": "Crossing Island",
                                  "time_zone": "Europe/London",
                                  "day_of_week": "Wednesday"}]
                            })])
def test_eventlist_dump(event_list, output):
    assert event_list.model_dump() == output
