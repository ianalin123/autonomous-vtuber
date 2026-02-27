import asyncio
import pytest
from twitch_client.priority_queue import PriorityMessageQueue
from core.interfaces import ChatMessage


@pytest.mark.asyncio
async def test_donation_has_higher_priority_than_chat():
    q = PriorityMessageQueue()
    regular = ChatMessage(username="user1", text="hi")
    donation = ChatMessage(username="donor", text="love you!", is_donation=True, donation_amount=5.0)
    await q.put(regular)
    await q.put(donation)
    first = await q.get()
    assert first.is_donation is True


@pytest.mark.asyncio
async def test_sub_has_higher_priority_than_regular():
    q = PriorityMessageQueue()
    regular = ChatMessage(username="user1", text="hi")
    sub = ChatMessage(username="subber", text="sub hype", is_sub=True, sub_tier=1)
    await q.put(regular)
    await q.put(sub)
    first = await q.get()
    assert first.is_sub is True


@pytest.mark.asyncio
async def test_queue_empty_initially():
    q = PriorityMessageQueue()
    assert q.empty() is True
