"""Bridge between Twitch priority queue and Open-LLM-VTuber WebSocket."""
import asyncio
import json
import websockets
from loguru import logger

from twitch_client.priority_queue import PriorityMessageQueue


OLV_WS_URL = "ws://localhost:12393/client-ws"
RECONNECT_DELAY = 5.0


class TwitchBridge:
    """Drains Twitch chat from the priority queue and forwards to Open-LLM-VTuber.

    Sends one message at a time and waits for `conversation-chain-end` before
    sending the next, so OLV always finishes responding before getting a new input.
    """

    def __init__(self, queue: PriorityMessageQueue) -> None:
        self._queue = queue
        self._ready = asyncio.Event()

    async def run(self) -> None:
        """Main run loop — reconnects whenever the OLV WebSocket drops."""
        while True:
            try:
                logger.info(f"[bridge] Connecting to {OLV_WS_URL}")
                async with websockets.connect(OLV_WS_URL) as ws:
                    logger.info("[bridge] Connected to Open-LLM-VTuber")
                    self._ready.set()  # fresh session — ready to accept first message

                    receiver = asyncio.create_task(self._receive_loop(ws))
                    sender = asyncio.create_task(self._send_loop(ws))

                    done, pending = await asyncio.wait(
                        [receiver, sender],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for t in pending:
                        t.cancel()
                        try:
                            await t
                        except asyncio.CancelledError:
                            pass
                    for t in done:
                        t.result()  # re-raise any exception from the finished task

            except Exception as e:
                logger.warning(
                    f"[bridge] Disconnected ({type(e).__name__}: {e}). "
                    f"Retrying in {RECONNECT_DELAY}s"
                )
                self._ready.clear()
                await asyncio.sleep(RECONNECT_DELAY)

    async def _receive_loop(self, ws) -> None:
        """Read OLV server messages; set ready when conversation ends."""
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            text = msg.get("text", "")

            if msg_type == "control" and text == "conversation-chain-end":
                logger.info("[bridge] OLV is idle — ready for next Twitch message")
                self._ready.set()
            elif msg_type == "backend-synth-complete":
                # OLV finished generating all TTS audio and is waiting for playback
                # confirmation before sending conversation-chain-end. Since we're
                # headless (no audio playback), ack immediately.
                logger.debug("[bridge] backend-synth-complete → sending frontend-playback-complete")
                await ws.send(json.dumps({"type": "frontend-playback-complete"}))
            elif msg_type == "full-text":
                logger.info(f"[bridge] OLV: {text!r}")
            elif msg_type == "error":
                logger.error(f"[bridge] OLV error: {msg}")

    async def _send_loop(self, ws) -> None:
        """Drain the priority queue and forward one message at a time to OLV."""
        while True:
            await self._ready.wait()
            msg = await self._queue.get()
            formatted = f"[{msg.username}]: {msg.text}"
            logger.info(f"[bridge] → OLV: {formatted!r}")
            self._ready.clear()  # mark busy until conversation-chain-end
            await ws.send(json.dumps({"type": "text-input", "text": formatted}))
