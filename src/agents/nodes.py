from datetime import datetime as dt

from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

from prompts.event_prompt import event_list_prompt
from models.agent_states import DatemarkAgentState
from models.agent_configs import DatemarkAgentConfig
from models.io_models import EventList

import logging
logger = logging.getLogger()


async def generate_events_list(
        state: DatemarkAgentState,
        runtime: Runtime[DatemarkAgentConfig],
):
    input_text = state["input_text"]

    model_w_structured_output = runtime.context["model"].with_structured_output(schema=EventList)

    logger.info(f"Processing the textual input: {input_text}")

    response = await model_w_structured_output.ainvoke(
        [
            HumanMessage(content=event_list_prompt.format(input_text=input_text,
                                                          current_year=dt.now().year))
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
