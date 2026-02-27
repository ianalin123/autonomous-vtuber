import asyncio
import twitchio
from core.config import settings
from core.event_bus import EventBus
from core.interfaces import Event, EventType, ChatMessage
from twitch_client.priority_queue import PriorityMessageQueue


class VTuberBot(twitchio.Client):
    def __init__(self, bus: EventBus, queue: PriorityMessageQueue) -> None:
        super().__init__(token=settings.twitch_oauth_token)
        self._bus = bus
        self._queue = queue

    async def event_ready(self) -> None:
        print(f"Bot ready | {self.nick}")
        await self.join_channels([settings.twitch_channel])

    async def event_message(self, message: twitchio.Message) -> None:
        if message.echo:
            return
        msg = ChatMessage(
            username=message.author.name,
            text=message.content,
            badges=[b.name for b in (message.author.badges or [])],
        )
        await self._queue.put(msg)
        await self._bus.publish(Event(
            type=EventType.CHAT_MESSAGE,
            payload={"username": msg.username, "text": msg.text},
            priority=1,
            source="twitch",
        ))


async def main() -> None:
    bus = EventBus()
    queue = PriorityMessageQueue()
    bot = VTuberBot(bus, queue)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
