import asyncio
from core.interfaces import ChatMessage


def _priority(msg: ChatMessage) -> int:
    if msg.is_donation:
        return int(msg.donation_amount * 10) + 1000
    if msg.is_sub:
        return (msg.sub_tier or 1) * 100
    if "moderator" in msg.badges:
        return 50
    return 1


class PriorityMessageQueue:
    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._counter = 0

    async def put(self, msg: ChatMessage) -> None:
        await self._queue.put((-_priority(msg), self._counter, msg))
        self._counter += 1

    async def get(self) -> ChatMessage:
        _, _, msg = await self._queue.get()
        return msg

    def empty(self) -> bool:
        return self._queue.empty()
