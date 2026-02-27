import pytest
from unittest.mock import MagicMock, patch


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
