from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.base import AgentBase
from agents.nodes import generate_events_list

from models.agent_states import DatemarkAgentState
from models.io_models import AgentResponse

import logging

logger = logging.getLogger()


def initialize_datemark_agent(checkpointer):

    workflow = StateGraph(DatemarkAgentState)

    workflow.add_node("generate_events_list", generate_events_list)

    workflow.set_entry_point("generate_events_list")
    workflow.add_edge("generate_events_list", END)

    graph = workflow.compile(
        checkpointer=checkpointer
    )

    return graph


class DatemarkAgent(AgentBase):

    def _init_agent(self) -> CompiledStateGraph:
        langgraph_agent_executor = initialize_datemark_agent(
            checkpointer=self.checkpointer,
        )

        return langgraph_agent_executor

    async def run_datemark_agent(self, input_text: str, thread_id: str):
        resp = await self.agent.ainvoke(
            dict(input_text=input_text),
            debug=False,
            context=dict(model=self.llm),
            config=dict(configurable={"thread_id": thread_id})

        )

        logger.info(f"Events found:\n{str(resp['event_list'])}")

        return AgentResponse(
            message="done",
            event_list=resp['event_list']
        )
