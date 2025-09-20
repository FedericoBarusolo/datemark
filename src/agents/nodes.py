from datetime import datetime as dt

from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime
from langgraph.types import interrupt

from src.prompts.event_prompt import event_list_prompt
from src.typing.agent_states import DatemarkAgentState
from src.typing.agent_configs import DatemarkAgentConfig
from src.typing.io_models import EventList

from src.services.google_authentication import create_oauth_flow_with_credentials
from src.services.google_calendar import create_calendar_event

import logging

logger = logging.getLogger()


async def generate_events_list(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
):
    input_text = state["input_text"]

    model_w_structured_output = runtime.context["model"].with_structured_output(schema=EventList)

    logger.info("Processing the textual input: {input_text}")

    response = await model_w_structured_output.ainvoke(
        [
            SystemMessage(content=event_list_prompt.format(input_text=input_text,
                                                           current_year=dt.now().year))
        ]
    )

    if not isinstance(response, EventList):
        logger.info(
            "The response from the model is not valid. Expected a SystemDetails."
        )
        raise ValueError("Invalid response from the model.")
    else:
        logger.info(f"Detected Events:\n{response.as_string()}")
        return {"event_list": response.events}


async def select_events_to_add(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
):

    result = interrupt(
        # Interrupt information to surface to the client.
        {
            "task": "Choose the event ids you want to insert."
        }
    )

    logger.info(f"Selected Events to load to calendar:\n{result["selected_events"].as_string()}")

    # Update the state with the edited text
    return {
        "selected_events": result["selected_events"]
    }


async def add_events_to_calendar(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
):
    events = state.get("selected_events", [])

    creds = create_oauth_flow_with_credentials()

    logger.info(f"Inserting the following Events:\n{events.as_string()}")

    for ev in events.events:
        create_calendar_event(creds, ev)

    return {"event_list": events}
