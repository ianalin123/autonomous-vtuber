import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.performer import Performer


@pytest.mark.asyncio
async def test_speak_calls_openai_tts():
    mock_response = MagicMock()
    mock_response.content = b"audio_bytes"
    with patch("agents.performer.AsyncOpenAI") as mock_openai_class:
        mock_instance = MagicMock()
        mock_instance.audio.speech.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_instance
        performer = Performer(frontend_url="http://localhost:12393")
        with patch("agents.performer.websockets.connect") as mock_ws:
            mock_ws_conn = AsyncMock()
            mock_ws_conn.__aenter__ = AsyncMock(return_value=AsyncMock(send=AsyncMock()))
            mock_ws_conn.__aexit__ = AsyncMock(return_value=False)
            mock_ws.return_value = mock_ws_conn
            await performer.speak("Hello chat!", emotion="happy")
            mock_instance.audio.speech.create.assert_called_once()


@pytest.mark.asyncio
async def test_emotion_maps_to_expression():
    performer = Performer(frontend_url="http://localhost:12393")
    assert performer._get_expression("happy") == "smile"
    assert performer._get_expression("sad") == "sad"
    assert performer._get_expression("neutral") == "idle"
