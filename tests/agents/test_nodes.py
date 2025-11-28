import pytest
from datetime import datetime as dt

from agents import nodes as nd
from models.io_models import Event, EventList
from models.agent_states import DatemarkAgentState
from models.agent_configs import DatemarkAgentConfig

from langgraph.runtime import Runtime

from tests import mock


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
                                              ), {},
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


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("state,runtime,output",
                         [(DatemarkAgentState(input_text="""
                                                           [{"title": "Cantina Band Concert", 
                                                             "start_time": "2025-01-01 20.00", 
                                                             "end_time": "2025-01-01 21.00", 
                                                             "time_zone": "Tatooine/Mos Eisley", 
                                                             "location": "Mos Eisley, Chalmun's Cantina"}]
                                                           """
                                              ),
                           Runtime(
                               context=dict(DatemarkAgentConfig.model_construct(model=mock.MockAgentModel()))),
                           DatemarkAgentState(event_list=EventList(events=[
                               Event.model_construct(title="Cantina Band Concert",
                                                     start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                     end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                     time_zone="Tatooine/Mos Eisley",
                                                     location="Mos Eisley, Chalmun's Cantina")
                           ]))
                           ),
                          (DatemarkAgentState(input_text="""
                                                           [{"title": "Cantina Band Concert", 
                                                             "start_time": "2025-01-01 20.00",
                                                             "time_zone": "Tatooine/Mos Eisley", 
                                                             "location": "Mos Eisley, Chalmun's Cantina"}]
                                                           """
                                              ),
                           Runtime(context=dict(DatemarkAgentConfig.model_construct(model=mock.MockAgentModel()))),
                           DatemarkAgentState(event_list=EventList(events=[
                               Event.model_construct(title="Cantina Band Concert",
                                                     start_time=dt.strptime("2025-01-01 20.00",
                                                                            "%Y-%m-%d %H.%M"),
                                                     time_zone="Tatooine/Mos Eisley",
                                                     location="Mos Eisley, Chalmun's Cantina")
                           ]))
                           ),
                          (DatemarkAgentState(input_text="""
                                                           [{"foo": "nonsensical content"}]
                                                           """
                                              ),
                           Runtime(context=dict(DatemarkAgentConfig.model_construct(model=mock.MockAgentModel()))),
                           ValueError
                           )])
async def test_generate_events_list(state, runtime, output, monkeypatch):
    monkeypatch.setattr(nd, "event_list_prompt", "{input_text}")

    if isinstance(output, type(Exception)):
        with pytest.raises(output, match="Invalid response from the model"):
            await nd.generate_events_list(state, runtime)
    else:
        assert await nd.generate_events_list(state, runtime) == output


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("state,runtime,output",
                         [(DatemarkAgentState(event_list=EventList(events=[
                             Event.model_construct(title="Cantina Band Concert#1",
                                                   start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                   end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                   time_zone="Tatooine/Mos Eisley",
                                                   location="Mos Eisley, Chalmun's Cantina"),

                             Event.model_construct(title="Cantina Band Concert#2",
                                                   start_time=dt.strptime("2025-01-02 21.00", "%Y-%m-%d %H.%M"),
                                                   end_time=dt.strptime("2025-01-02 23.00", "%Y-%m-%d %H.%M"),
                                                   time_zone="Tatooine/Mos Eisley",
                                                   location="Mos Eisley, Chalmun's Cantina")
                         ]),
                             user_query="""
                                                            [{"title": "Cantina Band Concert#1", 
                                                             "start_time": "2025-01-01 20.00", 
                                                             "end_time": "2025-01-01 21.00", 
                                                             "time_zone": "Tatooine/Mos Eisley", 
                                                             "location": "Mos Eisley, Chalmun's Cantina"}]
                                                """
                         ),
                           Runtime(
                               context=dict(DatemarkAgentConfig.model_construct(model=mock.MockAgentModel()))),
                           DatemarkAgentState(event_list=EventList(events=[
                               Event.model_construct(title="Cantina Band Concert#1",
                                                     start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                     end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                     time_zone="Tatooine/Mos Eisley",
                                                     location="Mos Eisley, Chalmun's Cantina")
                           ]))
                         ),
                             (DatemarkAgentState(event_list=EventList(events=[
                                 Event.model_construct(title="Cantina Band Concert#1",
                                                       start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                       end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                       time_zone="Tatooine/Mos Eisley",
                                                       location="Mos Eisley, Chalmun's Cantina"),

                                 Event.model_construct(title="Cantina Band Concert#2",
                                                       start_time=dt.strptime("2025-01-02 21.00", "%Y-%m-%d %H.%M"),
                                                       end_time=dt.strptime("2025-01-02 23.00", "%Y-%m-%d %H.%M"),
                                                       time_zone="Tatooine/Mos Eisley",
                                                       location="Mos Eisley, Chalmun's Cantina")
                             ]),
                                 user_query="""
                                                    Very nonsensical user query!!
                                                """
                             ),
                              Runtime(
                                  context=dict(DatemarkAgentConfig.model_construct(model=mock.MockAgentModel()))),
                              DatemarkAgentState(event_list=EventList(events=[
                                  Event.model_construct(title="Cantina Band Concert#1",
                                                        start_time=dt.strptime("2025-01-01 20.00", "%Y-%m-%d %H.%M"),
                                                        end_time=dt.strptime("2025-01-01 21.00", "%Y-%m-%d %H.%M"),
                                                        time_zone="Tatooine/Mos Eisley",
                                                        location="Mos Eisley, Chalmun's Cantina"),

                                  Event.model_construct(title="Cantina Band Concert#2",
                                                        start_time=dt.strptime("2025-01-02 21.00", "%Y-%m-%d %H.%M"),
                                                        end_time=dt.strptime("2025-01-02 23.00", "%Y-%m-%d %H.%M"),
                                                        time_zone="Tatooine/Mos Eisley",
                                                        location="Mos Eisley, Chalmun's Cantina")
                              ])
                              )
                             )])
async def test_filter_events_by_user_query(state, runtime, output, monkeypatch):
    monkeypatch.setattr(nd, "filter_events_by_user_query_prompt", "{user_query}")

    if isinstance(output, type(Exception)):
        with pytest.raises(output, match="Invalid response from the model"):
            await nd.filter_events_by_user_query(state, runtime)
    else:
        assert await nd.filter_events_by_user_query(state, runtime) == output
