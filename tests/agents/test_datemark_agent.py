import pytest
from agents import base
from agents.datemark_agent import DatemarkAgent

from tests import mock


@pytest.mark.unit
@pytest.mark.parametrize("nodes", [{"__start__",
                                    "preprocess_web_page",
                                    "generate_events_list",
                                    "filter_events_by_user_query",
                                    "validate_events"}])
def test_init_agent(nodes, monkeypatch):

    monkeypatch.setattr(base, "init_chat_model", mock.mock_init_chat_model)

    ag = DatemarkAgent()

    assert set(ag.agent.nodes.keys()) == nodes