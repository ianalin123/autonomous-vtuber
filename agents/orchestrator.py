"""Orchestrator agent — Claude tool-use loop for autonomous stream direction."""
from __future__ import annotations
import asyncio
from anthropic import Anthropic
from core.config import settings
from core.event_bus import EventBus
from core.interfaces import Event, EventType

TOOLS = [
    {
        "name": "get_stream_state",
        "description": "Returns current viewer count, chat velocity, donation rate, current activity",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "set_activity",
        "description": "Tell the Performer agent what activity to do next",
        "input_schema": {
            "type": "object",
            "properties": {
                "activity": {"type": "string", "enum": ["talk", "react", "game", "q_and_a", "idle"]},
                "topic": {"type": "string", "description": "Optional topic to discuss"},
            },
            "required": ["activity"],
        },
    },
    {
        "name": "send_chat_response",
        "description": "Dispatch a spoken response to Twitch chat via the Performer agent",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "emotion": {"type": "string", "enum": ["happy", "sad", "excited", "neutral", "angry"], "default": "neutral"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "get_analytics_summary",
        "description": "Get latest engagement metrics: revenue, viewer retention, chat velocity trends",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


class OrchestratorAgent:
    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        try:
            with open("persona/character.md") as f:
                self._system = f.read()
        except FileNotFoundError:
            self._system = "You are Aiko, an autonomous VTuber. Be engaging and entertaining."

    async def decide(self, context: str) -> list[dict]:
        response = self._client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=self._system + "\n\nYou are directing a live stream. Use tools to take actions.",
            tools=TOOLS,
            messages=[{"role": "user", "content": context}],
        )
        return [
            {"name": block.name, "input": block.input}
            for block in response.content
            if block.type == "tool_use"
        ]

    async def run_loop(self, bus: EventBus, poll_interval: float = 5.0) -> None:
        """Main orchestration loop — observe stream state, decide actions, dispatch."""
        while True:
            context = "Current stream state: idle. Chat is quiet. What should Aiko do?"
            tool_calls = await self.decide(context)
            for call in tool_calls:
                if call["name"] == "send_chat_response":
                    await bus.publish(Event(
                        type=EventType.SPEAK,
                        payload=call["input"],
                        priority=10,
                        source="orchestrator",
                    ))
                elif call["name"] == "set_activity":
                    await bus.publish(Event(
                        type=EventType.STREAM_STATE,
                        payload={"activity": call["input"].get("activity")},
                        priority=5,
                        source="orchestrator",
                    ))
            await asyncio.sleep(poll_interval)
