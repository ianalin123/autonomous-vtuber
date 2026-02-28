import asyncio
import signal
import uvicorn
import twitchio
from core.config import settings
from core.event_bus import EventBus
from core.interfaces import Event, EventType, ChatMessage
from core.bandit import ThompsonBandit, Action
from twitch_client.priority_queue import PriorityMessageQueue
from twitch_client.bridge import TwitchBridge
from agents.analytics import AnalyticsAgent, MetricsCollector, create_app
from agents.orchestrator import OrchestratorAgent
from agents.retrospective import StreamRetrospective

BANDIT_STATE_PATH = "data/bandit_state.json"


class VTuberBot(twitchio.Client):
    def __init__(self, bus: EventBus, queue: PriorityMessageQueue) -> None:
        super().__init__(token=settings.twitch_oauth_token)
        self._bus = bus
        self._queue = queue

    async def event_ready(self) -> None:
        print(f"[ready] nick={self.nick}")
        print(f"[ready] joining channel: {settings.twitch_channel!r}")
        await self.join_channels([settings.twitch_channel])
        print(f"[ready] joined OK")

    async def event_join(self, channel, user) -> None:
        print(f"[join] user={user.name} channel={channel.name}")

    async def event_message(self, message: twitchio.Message) -> None:
        print(f"[message] raw: author={message.author} echo={message.echo} content={message.content!r}")
        if message.echo:
            print("[message] skipped (echo)")
            return
        msg = ChatMessage(
            username=message.author.name,
            text=message.content,
            badges=list(message.author.badges or []),
        )
        print(f"[message] queued: {msg.username}: {msg.text!r} priority={msg.is_donation}/{msg.is_sub}")
        await self._queue.put(msg)
        await self._bus.publish(Event(
            type=EventType.CHAT_MESSAGE,
            payload={"username": msg.username, "text": msg.text},
            priority=1,
            source="twitch",
        ))
        print(f"[message] published to event bus OK")

    async def event_error(self, error: Exception, data: str = None) -> None:
        print(f"[error] {type(error).__name__}: {error} | data={data!r}")


async def run_retrospective(analytics: AnalyticsAgent, bandit: ThompsonBandit) -> None:
    """Run post-stream retrospective: summarize, update bandit, save state."""
    retro = StreamRetrospective(db=None, bandit=bandit)
    data = analytics.get_stream_summary_data()
    summary = retro.build_summary(
        stream_id="live",
        duration_minutes=data["duration_minutes"],
        peak_viewers=data["peak_viewers"],
        total_revenue=data["total_revenue"],
        top_activities=data["top_activities"],
        chat_messages=data["chat_messages"],
    )
    retro.update_bandit(summary)
    bandit.save(BANDIT_STATE_PATH)
    report = retro.format_report(summary)
    print("\n" + report + "\n")


async def main() -> None:
    bus = EventBus()
    queue = PriorityMessageQueue()
    collector = MetricsCollector()
    bandit = ThompsonBandit.load_or_create(BANDIT_STATE_PATH)

    analytics = AnalyticsAgent(bus, collector)
    orchestrator = OrchestratorAgent(
        collector=collector,
        bandit=bandit,
        bandit_save_path=BANDIT_STATE_PATH,
    )

    app = create_app(analytics)
    bot = VTuberBot(bus, queue)
    bridge = TwitchBridge(queue)

    shutdown_event = asyncio.Event()

    def _signal_handler() -> None:
        print("\n[shutdown] Signal received, running retrospective...")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)

    tasks = [
        asyncio.create_task(bridge.run(), name="bridge"),
        asyncio.create_task(analytics.broadcast_loop(), name="analytics-broadcast"),
        asyncio.create_task(
            orchestrator.run_loop(
                bus,
                current_activity_getter=lambda: analytics._current_activity,
            ),
            name="orchestrator",
        ),
        asyncio.create_task(server.serve(), name="uvicorn"),
        asyncio.create_task(bot.start(), name="twitch-bot"),
    ]

    print("[main] All systems started:")
    print(f"  - Twitch bot: {settings.twitch_channel}")
    print(f"  - Analytics API: http://0.0.0.0:8000")
    print(f"  - WebSocket: ws://0.0.0.0:8000/ws/metrics")
    print(f"  - Orchestrator: polling every 5s with bandit")
    print(f"  - Bridge: forwarding to Open-LLM-VTuber")

    await shutdown_event.wait()

    await run_retrospective(analytics, bandit)

    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    print("[main] Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
