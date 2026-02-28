import asyncio
import twitchio
from core.config import settings
from core.event_bus import EventBus
from core.interfaces import Event, EventType, ChatMessage
from twitch_client.priority_queue import PriorityMessageQueue
from twitch_client.bridge import TwitchBridge


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


async def main() -> None:
    bus = EventBus()
    queue = PriorityMessageQueue()
    bot = VTuberBot(bus, queue)
    bridge = TwitchBridge(queue)
    asyncio.create_task(bridge.run())
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
