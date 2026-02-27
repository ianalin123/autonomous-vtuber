import base64
import json
import websockets
from openai import AsyncOpenAI
from core.config import settings

EMOTION_VOICE_PARAMS: dict[str, dict] = {
    "happy": {"speed": 1.1},
    "sad": {"speed": 0.9},
    "excited": {"speed": 1.2},
    "neutral": {"speed": 1.0},
    "angry": {"speed": 1.05},
}

EMOTION_EXPRESSIONS: dict[str, str] = {
    "happy": "smile",
    "sad": "sad",
    "excited": "surprised",
    "neutral": "idle",
    "angry": "angry",
}


class Performer:
    def __init__(self, frontend_url: str) -> None:
        self._frontend_url = frontend_url.replace("http", "ws") + "/ws"
        self._openai = AsyncOpenAI(api_key=settings.openai_api_key)

    def _get_expression(self, emotion: str) -> str:
        return EMOTION_EXPRESSIONS.get(emotion, "idle")

    async def speak(self, text: str, emotion: str = "neutral") -> None:
        params = EMOTION_VOICE_PARAMS.get(emotion, EMOTION_VOICE_PARAMS["neutral"])
        response = await self._openai.audio.speech.create(
            model="tts-1",
            voice=settings.openai_tts_voice,
            input=text,
            speed=params["speed"],
        )
        audio_b64 = base64.b64encode(response.content).decode()
        expression = self._get_expression(emotion)
        async with websockets.connect(self._frontend_url) as ws:
            await ws.send(json.dumps({
                "type": "speak",
                "text": text,
                "audio": audio_b64,
                "expression": expression,
            }))

    async def set_expression(self, expression: str) -> None:
        async with websockets.connect(self._frontend_url) as ws:
            await ws.send(json.dumps({"type": "expression", "value": expression}))

    async def set_motion(self, motion: str) -> None:
        async with websockets.connect(self._frontend_url) as ws:
            await ws.send(json.dumps({"type": "motion", "value": motion}))
