import asyncio
import pytest
from core.interfaces import Event, EventType
from core.event_bus import EventBus


@pytest.mark.asyncio
async def test_publish_subscribe_roundtrip():
    bus = EventBus()
    received: list[Event] = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe(EventType.CHAT_MESSAGE, handler)
    event = Event(type=EventType.CHAT_MESSAGE, payload={"text": "hello"})
    await bus.publish(event)
    await asyncio.sleep(0.05)
    assert len(received) == 1
    assert received[0].payload["text"] == "hello"


@pytest.mark.asyncio
async def test_priority_ordering():
    bus = EventBus()
    order: list[int] = []

    async def handler(event: Event):
        order.append(event.priority)

    bus.subscribe(EventType.DONATION, handler)
    await bus.publish(Event(type=EventType.DONATION, payload={}, priority=1))
    await bus.publish(Event(type=EventType.DONATION, payload={}, priority=10))
    await asyncio.sleep(0.05)
    assert order == [1, 10]
