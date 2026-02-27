"""Orchestrator agent — Claude tool-use loop for stream direction."""
from anthropic import Anthropic
from core.config import settings

TOOLS = [
    {
        "name": "get_stream_state",
        "description": "Returns current viewer count, chat velocity, donation rate, current activity",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "set_activity",
        "description": "Tell the Performer agent what activity to do",
        "input_schema": {
            "type": "object",
            "properties": {
                "activity": {"type": "string", "enum": ["talk", "react", "game", "q_and_a", "idle"]}
            },
            "required": ["activity"],
        },
    },
    {
        "name": "send_chat_response",
        "description": "Dispatch a spoken response to Twitch chat via the Performer",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "emotion": {"type": "string", "default": "neutral"},
            },
            "required": ["text"],
        },
    },
]


class OrchestratorAgent:
    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        with open("persona/character.md") as f:
            self._system = f.read()

    async def decide(self, context: str) -> list[dict]:
        response = self._client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=self._system,
            tools=TOOLS,
            messages=[{"role": "user", "content": context}],
        )
        tool_calls = []
        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append({"name": block.name, "input": block.input})
        return tool_calls
