import asyncio
from collections import defaultdict
from typing import Callable, Awaitable
from core.interfaces import Event, EventType

Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        handlers = self._subscribers.get(event.type, [])
        await asyncio.gather(*(h(event) for h in handlers))
