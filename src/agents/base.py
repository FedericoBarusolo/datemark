import logging
from abc import abstractmethod

from langchain_core.tools import BaseToolkit
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langchain.chat_models import init_chat_model

from models.io_models import available_llm_models, available_llm_providers, AgentResponse

logger = logging.getLogger(__name__)


class AgentBase:

    def __init__(
        self,
        temperature: float = 0.0,
        llm_provider: available_llm_providers = "groq",
        llm_model: available_llm_models = "llama-3.3-70b-versatile",
        debug: bool = False,
        checkpointer: BaseCheckpointSaver | None = None,
    ):
        # settings
        self.debug = debug
        self.checkpointer = checkpointer

        # LLM parameters
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature

        self.llm = init_chat_model(self.llm_model, model_provider=self.llm_provider, temperature=0)

        self.toolkit = self._init_toolkit()

        self.agent = self._init_agent()

    @abstractmethod
    def _invoke_agent(self, *_args, **_kwargs) -> AgentResponse:
        """invoke agent"""
        raise NotImplementedError()

    @abstractmethod
    async def _ainvoke_agent(self, *_args, **_kwargs) -> AgentResponse:
        """async agent invocation"""
        raise NotImplementedError()

    @abstractmethod
    def _init_agent(self) -> CompiledStateGraph:
        "initialize agent"

    @abstractmethod
    def _init_toolkit(self) -> BaseToolkit:
        "initialize toolkit"
