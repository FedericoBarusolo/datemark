from datetime import datetime
from typing import List, Literal, Optional
import pytz as tz

from pydantic import BaseModel


available_llm_providers = Literal["groq", "openai", "anthropic", "google_vertexai"]
available_llm_models = Literal["llama-3.1-8b-instant",
                               "llama-3.3-70b-versatile",
                               "openai/gpt-oss-120b",
                               "gpt-4o-mini",
                               "claude-3-5-haiku-latest"]

TimezoneType = Literal[tuple(tz.all_timezones)]


class Event(BaseModel):
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    time_zone: TimezoneType = None
    location: str | None

    def __str__(self):
        result = ""

        result += f"Title: {self.title}\n"
        result += f"Start Time: {self.start_time}\n"
        result += f"End Time: {self.end_time}\n"
        result += f"Location: {self.location}\n"

        return result

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        else:
            data['end_time'] = None
        data["day_of_week"] = self.start_time.strftime("%A")
        data["day_of_week"] = self.start_time.strftime("%A")  # Enables filtering based on weekend yes/no
        return data


class EventList(BaseModel):
    events: List[Event]

    def __str__(self):
        result = ""

        for ev in self.events:
            result += str(ev)
            result += "-" * 20 + "\n"

        return result

    def model_dump(self, **kwargs):
        return {
            'events': [event.model_dump(**kwargs) for event in self.events]
        }


class AgentResponse(BaseModel):
    message: str
    event_list: EventList
