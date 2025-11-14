import pytest
from datetime import datetime as dt

from agents import nodes as nd
from models.io_models import Event, EventList
from models.agent_states import DatemarkAgentState


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("event,output",
                         [
                             # Happy path: dates are valid
                             (Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina"),
                              Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina")),

                             # Happy path: dates are equal but still valid
                             (Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina"),
                              Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina")),

                             # Unhappy path: end is same day before start
                             (Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 19.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina"),
                              Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina")),

                             # Unhappy path: end is the day before start
                             (Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-02 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina"),
                              Event.model_construct(title="Cantina Band Concert",
                                                    start_time=dt.strptime("2025-01-02 20.00", "%Y-%m-%d %H.%M"),
                                                    end_time=dt.strptime("2025-01-02 21.00", "%Y-%m-%d %H.%M"),
                                                    time_zone="Tatooine/Mos Eisley",
                                                    location="Mos Eisley, Chalmun's Cantina")
                              )])
async def test_validate_event_times(event, output):
    assert output == await nd.validate_event_times(event)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("state,runtime,output",
                         [(DatemarkAgentState(input_text="",
                                              event_list=EventList(events=[
                                                  Event.model_construct(title="Cantina Band Concert#1",
                                                                        start_time=dt.strptime("2025-01-01 "
                                                                                               "20.00",
                                                                                               "%Y-%m-%d %H.%M"),
                                                                        end_time=dt.strptime("2025-01-01 "
                                                                                             "21.00",
                                                                                             "%Y-%m-%d %H.%M"),
                                                                        time_zone="Tatooine/Mos Eisley",
                                                                        location="Mos Eisley, Chalmun's Cantina"),
                                                  Event.model_construct(title="Cantina Band Concert#2",
                                                                        start_time=dt.strptime("2025-01-02 "
                                                                                               "20.00",
                                                                                               "%Y-%m-%d %H.%M"),
                                                                        end_time=dt.strptime("2025-01-02 "
                                                                                             "19.00",
                                                                                             "%Y-%m-%d %H.%M"),
                                                                        time_zone="Tatooine/Mos Eisley",
                                                                        location="Mos Eisley, Chalmun's Cantina")])
                                              ),{},
                           {"event_list": EventList(events=[
                                                  Event.model_construct(title="Cantina Band Concert#1",
                                                                        start_time=dt.strptime("2025-01-01 "
                                                                                               "20.00",
                                                                                               "%Y-%m-%d %H.%M"),
                                                                        end_time=dt.strptime("2025-01-01 "
                                                                                             "21.00",
                                                                                             "%Y-%m-%d %H.%M"),
                                                                        time_zone="Tatooine/Mos Eisley",
                                                                        location="Mos Eisley, Chalmun's Cantina"),
                                                  Event.model_construct(title="Cantina Band Concert#2",
                                                                        start_time=dt.strptime("2025-01-02 "
                                                                                               "20.00",
                                                                                               "%Y-%m-%d %H.%M"),
                                                                        end_time=dt.strptime("2025-01-02 "
                                                                                             "21.00",
                                                                                             "%Y-%m-%d %H.%M"),
                                                                        time_zone="Tatooine/Mos Eisley",
                                                                        location="Mos Eisley, Chalmun's Cantina")])})])
async def test_validate_events(state, runtime, output):
    assert output == await nd.validate_events(state, runtime)
