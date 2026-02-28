"""Analytics agent — metrics collection, event bus wiring, WebSocket broadcasting."""
from __future__ import annotations
import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from core.event_bus import EventBus
from core.interfaces import Event, EventType


def compute_engagement_score(
    chat_velocity: float,
    viewer_retention: float,
    donation_rate: float,
    weights: tuple[float, float, float] = (0.4, 0.4, 0.2),
) -> float:
    cv_norm = min(chat_velocity / 100.0, 1.0)
    return round(
        (cv_norm * weights[0] + viewer_retention * weights[1] + min(donation_rate, 1.0) * weights[2]) * 100,
        2,
    )


@dataclass
class MetricsCollector:
    viewer_count: int = 0
    chat_velocity: float = 0.0
    donations_per_hour: float = 0.0
    _message_count: int = field(default=0, repr=False)
    _donation_total: float = field(default=0.0, repr=False)
    _window_start: float = field(default_factory=time.time, repr=False)

    def record_chat_message(self) -> None:
        self._message_count += 1
        elapsed_minutes = (time.time() - self._window_start) / 60 or 1
        self.chat_velocity = round(self._message_count / elapsed_minutes, 2)

    def record_donation(self, amount: float) -> None:
        self._donation_total += amount
        elapsed_hours = (time.time() - self._window_start) / 3600 or 1
        self.donations_per_hour = round(self._donation_total / elapsed_hours, 2)

    def update_viewer_count(self, count: int) -> None:
        self.viewer_count = count

    def snapshot(self) -> dict:
        return {
            "viewer_count": self.viewer_count,
            "chat_velocity": self.chat_velocity,
            "donations_per_hour": self.donations_per_hour,
            "engagement_score": compute_engagement_score(
                self.chat_velocity,
                viewer_retention=min(self.viewer_count / 100, 1.0),
                donation_rate=min(self.donations_per_hour / 10, 1.0),
            ),
        }


class AnalyticsAgent:
    """Subscribes to the event bus, updates metrics, broadcasts to dashboard via WebSocket."""

    def __init__(self, bus: EventBus, collector: MetricsCollector | None = None) -> None:
        self._bus = bus
        self._collector = collector or MetricsCollector()
        self._clients: set[WebSocket] = set()
        self._current_activity: str = "idle"
        self._subs_count: int = 0
        self._is_live: bool = False
        self._stream_start: float = time.time()
        self._subscribe()

    @property
    def collector(self) -> MetricsCollector:
        return self._collector

    def _subscribe(self) -> None:
        self._bus.subscribe(EventType.CHAT_MESSAGE, self._on_chat)
        self._bus.subscribe(EventType.DONATION, self._on_donation)
        self._bus.subscribe(EventType.SUBSCRIPTION, self._on_subscription)
        self._bus.subscribe(EventType.VIEWER_COUNT, self._on_viewer_count)
        self._bus.subscribe(EventType.STREAM_STATE, self._on_stream_state)

    async def _on_chat(self, event: Event) -> None:
        self._collector.record_chat_message()
        self._is_live = True

    async def _on_donation(self, event: Event) -> None:
        amount = event.payload.get("amount", 0.0)
        username = event.payload.get("username", "anonymous")
        self._collector.record_donation(amount)
        self._is_live = True

        now = datetime.now(timezone.utc).isoformat()
        await self._broadcast({
            "type": "donation",
            "data": {
                "id": f"d_{uuid.uuid4().hex[:8]}",
                "username": username,
                "amount": amount,
                "message": event.payload.get("message", ""),
                "timestamp": now,
                "type": "donation",
            },
        })
        await self._broadcast({
            "type": "revenue_point",
            "data": {
                "timestamp": now,
                "amount": amount,
                "cumulative": self._collector._donation_total,
            },
        })

    async def _on_subscription(self, event: Event) -> None:
        self._subs_count += 1
        username = event.payload.get("username", "anonymous")
        self._is_live = True

        now = datetime.now(timezone.utc).isoformat()
        tier = event.payload.get("tier", 1)
        sub_value = {1: 4.99, 2: 9.99, 3: 24.99}.get(tier, 4.99)
        self._collector.record_donation(sub_value)

        await self._broadcast({
            "type": "donation",
            "data": {
                "id": f"s_{uuid.uuid4().hex[:8]}",
                "username": username,
                "amount": sub_value,
                "message": f"Tier {tier} subscription",
                "timestamp": now,
                "type": "sub",
            },
        })
        await self._broadcast({
            "type": "revenue_point",
            "data": {
                "timestamp": now,
                "amount": sub_value,
                "cumulative": self._collector._donation_total,
            },
        })

    async def _on_viewer_count(self, event: Event) -> None:
        count = event.payload.get("count", 0)
        self._collector.update_viewer_count(count)
        self._is_live = True

    async def _on_stream_state(self, event: Event) -> None:
        activity = event.payload.get("activity")
        if activity:
            self._current_activity = activity

    def _format_uptime(self) -> str:
        elapsed = int(time.time() - self._stream_start)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def _stream_state_msg(self) -> dict:
        snap = self._collector.snapshot()
        return {
            "type": "stream_state",
            "data": {
                "isLive": self._is_live,
                "viewerCount": snap["viewer_count"],
                "uptime": self._format_uptime(),
                "currentActivity": self._current_activity,
                "chatVelocity": snap["chat_velocity"],
                "engagementScore": snap["engagement_score"],
            },
        }

    def _metrics_update_msg(self) -> dict:
        return {
            "type": "metrics_update",
            "data": {
                "revenueToday": self._collector._donation_total,
                "subsCount": self._subs_count,
                "bitsToday": 0,
                "donationsPerHour": self._collector.donations_per_hour,
            },
        }

    async def _broadcast(self, message: dict) -> None:
        if not self._clients:
            return
        raw = json.dumps(message)
        dead: set[WebSocket] = set()
        for ws in self._clients:
            try:
                await ws.send_text(raw)
            except Exception:
                dead.add(ws)
        self._clients -= dead

    async def broadcast_loop(self, interval: float = 2.0) -> None:
        """Periodically push stream_state + metrics_update to all connected dashboards."""
        while True:
            await self._broadcast(self._stream_state_msg())
            await self._broadcast(self._metrics_update_msg())
            await asyncio.sleep(interval)

    async def handle_ws(self, ws: WebSocket) -> None:
        """Accept a dashboard WebSocket connection and keep it alive."""
        await ws.accept()
        self._clients.add(ws)
        try:
            await ws.send_text(json.dumps(self._stream_state_msg()))
            await ws.send_text(json.dumps(self._metrics_update_msg()))
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            self._clients.discard(ws)

    def get_stream_summary_data(self) -> dict:
        """Return data for building a StreamSummary at end of stream."""
        elapsed_min = (time.time() - self._stream_start) / 60
        return {
            "duration_minutes": round(elapsed_min, 1),
            "peak_viewers": self._collector.viewer_count,
            "total_revenue": self._collector._donation_total,
            "top_activities": [self._current_activity],
            "chat_messages": self._collector._message_count,
        }


def create_app(agent: AnalyticsAgent | None = None) -> FastAPI:
    """Build the FastAPI app. If no agent provided, creates a standalone one."""
    _app = FastAPI(title="Aiko Analytics API")
    _app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    if agent is None:
        _bus = EventBus()
        agent = AnalyticsAgent(_bus)

    _app.state.agent = agent
    collector = agent.collector

    @_app.websocket("/ws/metrics")
    async def ws_metrics(ws: WebSocket) -> None:
        await agent.handle_ws(ws)

    @_app.get("/api/stream/state")
    def get_stream_state() -> dict:
        return collector.snapshot()

    @_app.get("/api/revenue/summary")
    def get_revenue_summary() -> dict:
        return {
            "total_today": collector._donation_total,
            "donations_per_hour": collector.donations_per_hour,
            "sources": {"donations": collector._donation_total, "bits": 0, "subs": 0},
        }

    @_app.get("/api/viewers/top")
    def get_top_viewers() -> dict:
        return {"top_donors": [], "top_chatters": []}

    @_app.get("/api/streams/history")
    def get_stream_history() -> dict:
        return {"streams": []}

    @_app.get("/api/optimization/report")
    def get_optimization_report() -> dict:
        if hasattr(agent, '_bandit') and agent._bandit:
            return {"bandit_state": agent._bandit.state(), "recommendations": []}
        return {"last_updated": None, "recommendations": [], "bandit_state": "not_initialized"}

    @_app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return _app


# Module-level app for `uvicorn agents.analytics:app` compatibility
app = create_app()
