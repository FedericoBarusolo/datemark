from pydantic_settings import BaseSettings
from langchain_core.language_models import BaseChatModel


class DatemarkAgentConfig(BaseSettings):
    """Configurations for DPMInteractor"""

    model: BaseChatModel
