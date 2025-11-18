from typing import TypedDict

from models.io_models import EventList


class BaseAgentState(TypedDict):
    foo: str


class DatemarkAgentState(BaseAgentState):
    input_text: str
    user_query: str | None
    event_list: EventList
    selected_events: EventList
