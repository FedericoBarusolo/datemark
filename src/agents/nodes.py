import re
import asyncio
from datetime import timedelta
from datetime import datetime as dt

from markdownify import markdownify as md

from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

from prompts.event_prompt import (event_list_prompt,
                                  filter_events_by_user_query_prompt)
from models.agent_states import DatemarkAgentState
from models.agent_configs import DatemarkAgentConfig
from models.io_models import Event, EventList

from utils import constants as cst
from utils import html_parse as html

import logging
logger = logging.getLogger()


async def preprocess_web_page(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
) -> dict[str, str]:
    """
    Preprocess HTML content by removing unwanted tags and converting to markdown,
    in order to minimize content size for optimized tokenization while keeping useful
    content structure.

    Cleans HTML by removing script, style, navigation, and other non-content elements,
    then converts the remaining content to markdown format with normalized whitespace.

    Args:
        state: The current agent state containing the input HTML text to process.
        runtime: The runtime context (unused but required by node signature).

    Returns:
        A dictionary with key "input_text" containing the cleaned markdown content.
    """
    input_html = state["input_text"]

    # clean input html
    input_html = html.clean_html_string(input_html)

    # Convert html to markdown
    markdown = md(input_html)

    # Remove multiple blank lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    # Remove trailing whitespace
    markdown = '\n'.join(line.rstrip() for line in markdown.split('\n'))

    # Ensure single newline at end
    markdown = markdown.rstrip() + '\n'

    return {"input_text": markdown}


async def generate_events_list(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
) -> dict[str, EventList]:
    """
    Generate a list of events from textual input using an LLM.

    Processes natural language text to extract structured event information
    including titles, times, locations, and time zones.

    Args:
        state: The current agent state containing the input text to process.
        runtime: The runtime context containing the configured LLM model.

    Returns:
        A dictionary with key 'event_list' containing the extracted EventList.

    Raises:
        ValueError: If the model response is not a valid EventList instance.
    """
    input_text = state["input_text"]

    model_w_structured_output = runtime.context["model"].with_structured_output(schema=EventList)

    logger.info(f"Processing the textual input: {input_text[:500]}")

    current_time = dt.now()
    response = await model_w_structured_output.ainvoke(
        [
            HumanMessage(content=event_list_prompt.format(input_text=input_text,
                                                          current_date=current_time.strftime(cst.DATE_STANDARD_FMT),
                                                          current_year=current_time.year))
        ]
    )

    if not isinstance(response, EventList):
        logger.info(
            "The response from the model is not valid. Expected a SystemDetails."
        )
        raise ValueError("Invalid response from the model.")
    else:
        logger.info(f"Detected Events:\n{str(response)}")
        return {"event_list": response}


async def filter_events_by_user_query(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
) -> dict[str, EventList]:

    """
    Filter events based on a user's natural language query.

    Uses an LLM to intelligently filter the event list according to the
    user's query criteria. The model interprets the query and returns only
    events that match the user's intent.

    Args:
        state: The current agent state containing the event list to filter
            and the user query to apply.
        runtime: The runtime context containing the configured LLM model.

    Returns:
        A dictionary with key 'event_list' containing the filtered EventList.

    Raises:
        ValueError: If the model response is not a valid EventList instance.
    """
    event_list = state["event_list"]
    user_query = state["user_query"]

    model_w_structured_output = runtime.context["model"].with_structured_output(schema=EventList)

    logger.info(f"Filtering events based on user query: {user_query}")

    current_time = dt.now()
    try:
        response = await model_w_structured_output.ainvoke(
            [
                HumanMessage(content=filter_events_by_user_query_prompt.format(event_list=event_list.model_dump(),
                                                                               user_query=user_query,
                                                                               current_date=current_time.strftime(
                                                                                   cst.DATE_STANDARD_FMT)))
            ]
        )
    except Exception as e:
        logger.info(
            f"Error generating response: {e}"
        )
        return {"event_list": event_list}

    if not isinstance(response, EventList):
        logger.info(
            "The response from the model is not valid. Expected a SystemDetails."
        )
        return {"event_list": event_list}
    else:
        logger.info(f"Filtered Events:\n{str(response)}")
        return {"event_list": response}


async def validate_event_times(event: Event) -> Event:
    """
    Validate and correct event time constraints.

    Ensures that the event's end time is not before its start time. If the
    end time is invalid, it is automatically adjusted to be 1 hour after
    the start time.

    Args:
        event: The event to validate and potentially correct.

    Returns:
        The validated event with corrected end time if necessary.
    """
    if event.end_time is None or event.end_time < event.start_time:
        event.end_time = event.start_time + timedelta(hours=1)
    return event


async def validate_events(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
) -> dict[str, EventList]:
    """
    Validate all events in the state concurrently.

    Applies time validation to all events in the event list simultaneously
    using asyncio.gather for optimal performance.

    Args:
        state: The current agent state containing the event list to validate.
        runtime: The runtime context (unused but required by node signature).

    Returns:
        A dictionary with key "event_list" containing the validated EventList.
    """
    event_list = state["event_list"]

    # Apply validate_event_times to all events concurrently
    validated_events = await asyncio.gather(
        *[validate_event_times(event) for event in event_list.events]
    )

    return {"event_list": EventList(events=validated_events)}