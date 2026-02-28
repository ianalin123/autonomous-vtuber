import pytest
from unittest.mock import MagicMock, patch

from agents.analytics import MetricsCollector
from core.bandit import ThompsonBandit, Action


def test_orchestrator_returns_tool_calls():
    with patch("agents.orchestrator.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_block = MagicMock()
        mock_block.type = "tool_use"
        mock_block.name = "send_chat_response"
        mock_block.input = {"text": "hello chat!", "emotion": "happy"}
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response

        from agents.orchestrator import OrchestratorAgent
        agent = OrchestratorAgent()
        import asyncio
        calls = asyncio.run(agent.decide("viewer count is 100"))
        assert len(calls) == 1
        assert calls[0]["name"] == "send_chat_response"


def test_orchestrator_ignores_text_blocks():
    with patch("agents.orchestrator.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "just thinking..."
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response

        from agents.orchestrator import OrchestratorAgent
        agent = OrchestratorAgent()
        import asyncio
        calls = asyncio.run(agent.decide("idle stream"))
        assert calls == []


def test_orchestrator_builds_context_with_metrics():
    with patch("agents.orchestrator.Anthropic"):
        from agents.orchestrator import OrchestratorAgent
        collector = MetricsCollector()
        collector.update_viewer_count(42)
        collector.record_chat_message()
        agent = OrchestratorAgent(collector=collector)
        context = agent._build_context(current_activity="talk")
        assert "42 viewers" in context
        assert "talk" in context


def test_orchestrator_builds_context_with_bandit():
    with patch("agents.orchestrator.Anthropic"):
        from agents.orchestrator import OrchestratorAgent
        collector = MetricsCollector()
        bandit = ThompsonBandit(list(Action))
        agent = OrchestratorAgent(collector=collector, bandit=bandit)
        context = agent._build_context()
        assert "suggests" in context


def test_orchestrator_builds_fallback_context_without_collector():
    with patch("agents.orchestrator.Anthropic"):
        from agents.orchestrator import OrchestratorAgent
        agent = OrchestratorAgent()
        context = agent._build_context()
        assert "idle" in context.lower()


def test_orchestrator_records_action_to_bandit():
    with patch("agents.orchestrator.Anthropic"):
        from agents.orchestrator import OrchestratorAgent
        collector = MetricsCollector()
        collector.update_viewer_count(50)
        bandit = ThompsonBandit(list(Action))
        agent = OrchestratorAgent(collector=collector, bandit=bandit)
        initial_alpha = bandit._arms[Action.QA]["alpha"]
        agent._record_action("q_and_a")
        assert bandit._arms[Action.QA]["alpha"] != initial_alpha or bandit._arms[Action.QA]["beta"] != 1.0
