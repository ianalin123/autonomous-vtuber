"""Orchestrator agent — Claude tool-use loop for autonomous stream direction."""
from __future__ import annotations
import asyncio
from anthropic import Anthropic
from core.config import settings
from core.event_bus import EventBus
from core.interfaces import Event, EventType
from core.bandit import ThompsonBandit, Action
from agents.analytics import MetricsCollector

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
    def __init__(
        self,
        collector: MetricsCollector | None = None,
        bandit: ThompsonBandit | None = None,
        bandit_save_path: str | None = None,
    ) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._collector = collector
        self._bandit = bandit
        self._bandit_save_path = bandit_save_path
        try:
            with open("persona/character.md") as f:
                self._system = f.read()
        except FileNotFoundError:
            self._system = "You are Aiko, an autonomous VTuber. Be engaging and entertaining."

    def _build_context(self, current_activity: str = "idle") -> str:
        if self._collector is None:
            return "Current stream state: idle. Chat is quiet. What should Aiko do?"

        snap = self._collector.snapshot()
        parts = [
            f"Stream state: {snap['viewer_count']} viewers, "
            f"chat velocity {snap['chat_velocity']} msg/min, "
            f"engagement {snap['engagement_score']}/100, "
            f"revenue ${snap['donations_per_hour']:.1f}/hr.",
            f"Current activity: {current_activity}.",
        ]

        if self._bandit:
            suggested = self._bandit.select()
            parts.append(
                f"The optimization system suggests trying: {suggested.value}. "
                f"You can follow or override this suggestion."
            )

        parts.append("Based on this, what should Aiko do next?")
        return " ".join(parts)

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

    def _record_action(self, action_name: str) -> None:
        if not self._bandit:
            return
        action_map = {
            "talk": Action.TALK,
            "react": Action.REACT,
            "game": Action.GAME,
            "q_and_a": Action.QA,
            "idle": Action.IDLE,
        }
        action = action_map.get(action_name)
        if action:
            reward = 0.0
            if self._collector:
                snap = self._collector.snapshot()
                reward = min(snap["engagement_score"] / 100, 1.0)
            self._bandit.update(action, reward)
            if self._bandit_save_path:
                self._bandit.save(self._bandit_save_path)

    async def run_loop(
        self,
        bus: EventBus,
        poll_interval: float = 5.0,
        current_activity_getter=None,
    ) -> None:
        """Main orchestration loop — observe stream state, decide actions, dispatch."""
        while True:
            activity = current_activity_getter() if current_activity_getter else "idle"
            context = self._build_context(current_activity=activity)
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
                    chosen = call["input"].get("activity", "idle")
                    await bus.publish(Event(
                        type=EventType.STREAM_STATE,
                        payload={"activity": chosen},
                        priority=5,
                        source="orchestrator",
                    ))
                    self._record_action(chosen)
            await asyncio.sleep(poll_interval)
