from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.base import AgentBase
from agents.nodes import (generate_events_list,
                          validate_events,
                          filter_events_by_user_query)

from models.agent_states import DatemarkAgentState
from models.io_models import AgentResponse

import logging

logger = logging.getLogger()


def initialize_datemark_agent(checkpointer) -> CompiledStateGraph:
    """
    Initialize and compile the Datemark agent workflow graph.

    Creates a LangGraph workflow with nodes for event generation and validation,
    connected in a linear pipeline.

    Args:
        checkpointer: The checkpointer instance for persisting agent state
            across executions.

    Returns:
        A compiled state graph ready for execution.
    """
    workflow = StateGraph(DatemarkAgentState)

    workflow.add_node("generate_events_list", generate_events_list)
    workflow.add_node("filter_events_by_user_query", filter_events_by_user_query)
    workflow.add_node("validate_events", validate_events)

    workflow.set_entry_point("generate_events_list")
    workflow.add_conditional_edges("generate_events_list",
                                   lambda state: state.get("user_query") is not None,
                                   {
                                       True: "filter_events_by_user_query",
                                       False: "validate_events",
                                   })
    workflow.add_edge("filter_events_by_user_query", "validate_events")
    workflow.add_edge("validate_events", END)

    graph = workflow.compile(
        checkpointer=checkpointer
    )

    return graph


class DatemarkAgent(AgentBase):
    """
    Agent for extracting and validating calendar events from natural language text.

    The DatemarkAgent processes textual input to identify events, extract their
    details (title, time, location, timezone), and validate the extracted information
    before returning structured event data.

    Attributes:
        agent: The compiled LangGraph state graph executor.
        llm: The language model instance used for event extraction.
        checkpointer: The checkpointer for state persistence.
    """

    def _init_agent(self) -> CompiledStateGraph:
        """Initialize the internal LangGraph agent executor.

        Returns:
            The compiled state graph for the Datemark agent workflow.
        """
        langgraph_agent_executor = initialize_datemark_agent(
            checkpointer=self.checkpointer,
        )

        return langgraph_agent_executor

    async def run_datemark_agent(self, input_text: str, thread_id: str, user_query: str | None = None) -> AgentResponse:
        """
        Execute the Datemark agent to extract and validate events from text.

        Processes the input text through the complete agent pipeline: event
        extraction using an LLM, followed by validation of event time constraints.

        Args:
            input_text: The natural language text containing event information
                to extract.
            thread_id: Unique identifier for the conversation thread, used for
                state persistence across multiple invocations.
            user_query: A natural language user query containing conditions for
                events filtering.

        Returns:
            An AgentResponse containing a success message and the extracted,
            validated event list.
        """
        agent_payload = dict(input_text=input_text)
        if user_query is not None:
            agent_payload.update(dict(user_query=user_query))

        resp = await self.agent.ainvoke(
            agent_payload,
            debug=False,
            context=dict(model=self.llm),
            config=dict(configurable={"thread_id": thread_id})

        )

        logger.info(f"Events found:\n{str(resp['event_list'])}")

        return AgentResponse(
            message="done",
            event_list=resp['event_list']
        )