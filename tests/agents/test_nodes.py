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
    assert await nd.validate_event_times(event) == output


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
                                                  # End time before start time
                                                  Event.model_construct(title="Cantina Band Concert#2",
                                                                        start_time=dt.strptime("2025-01-02 "
                                                                                               "20.00",
                                                                                               "%Y-%m-%d %H.%M"),
                                                                        end_time=dt.strptime("2025-01-02 "
                                                                                             "19.00",
                                                                                             "%Y-%m-%d %H.%M"),
                                                                        time_zone="Tatooine/Mos Eisley",
                                                                        location="Mos Eisley, Chalmun's Cantina"),
                                                  # Missing end time
                                                  Event.model_construct(title="Cantina Band Concert#3",
                                                                        start_time=dt.strptime("2025-01-02 "
                                                                                               "20.00",
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
                                                                        location="Mos Eisley, Chalmun's Cantina"),
                                                  Event.model_construct(title="Cantina Band Concert#3",
                                                                        start_time=dt.strptime("2025-01-02 "
                                                                                               "20.00",
                                                                                               "%Y-%m-%d %H.%M"),
                                                                        end_time=dt.strptime("2025-01-02 "
                                                                                             "21.00",
                                                                                             "%Y-%m-%d %H.%M"),
                                                                        time_zone="Tatooine/Mos Eisley",
                                                                        location="Mos Eisley, Chalmun's Cantina")])})])
async def test_validate_events(state, runtime, output):
    assert await nd.validate_events(state, runtime) == output


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("state,runtime,output",
                         [
                             (DatemarkAgentState(input_text="""
                             <html>
                                 <head>
                                     <script>console.log('remove me');</script>
                                     <style>.class { color: red; }</style>
                                     <meta charset="UTF-8">
                                     <link rel="stylesheet" href="style.css">
                                 </head>
                                 <body>
                                     <header>Header content</header>
                                     <nav>Navigation</nav>
                                     <div>Big Big Concert</div>
                                     <p>Event description here.</p>
                                     <div class="jet-listing-dynamic-field__content">London<br>O2</div>
                                     <div class="jet-listing jet-listing-dynamic-field display-inline">
                                        <div class="jet-listing-dynamic-field__inline-wrap">
                                            <div class="jet-listing-dynamic-field__content">1 january 2025</div>
                                        </div>
                                     </div>	
                                     <img src="image.jpg" alt="image">
                                     <footer>Footer content</footer>
                                     <iframe src="external.html"></iframe>
                                     <noscript>No JS content</noscript>
                                     <svg><circle/></svg>
                                 </body>
                             </html>
                             """),
                              {},
                              {"input_text": "Big Big Concert\n\n"
                                             "Event description here.\n\n"
                                             "London\nO2\n\n"
                                             "1 january 2025\n"}),

                             (DatemarkAgentState(input_text="<html><body><p>Simple text</p></body></html>"),
                              {},
                              {"input_text": "Simple text\n"}),
                         ])
async def test_preprocess_web_page(state, runtime, output):
    assert await nd.preprocess_web_page(state, runtime) == output
