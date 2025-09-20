from pydantic import AwareDatetime
from typing import List, Literal
import pytz as tz

from pydantic import BaseModel


available_llm_providers = Literal["openai"]
available_llm_models = Literal["gpt-4o-mini"]

TimezoneType = Literal[tuple(tz.all_timezones)]


class Event(BaseModel):
    title: str
    start_time: AwareDatetime
    end_time: AwareDatetime
    time_zone: TimezoneType
    location: str | None

    def as_string(self):
        result = ""

        result += f"Title: {self.title}\n"
        result += f"Start Time: {self.start_time}\n"
        result += f"End Time: {self.end_time}\n"
        result += f"Location: {self.location}\n"

        return result


class EventList(BaseModel):
    events: List[Event]

    def as_string(self):
        result = ""

        for ev in self.events:
            result += ev.as_string()
            result += "-" * 20 + "\n"

        return result


class AgentResponse(BaseModel):
    message: str
