"""Analytics agent — metrics collection and FastAPI REST endpoints."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


# FastAPI app
_collector = MetricsCollector()
app = FastAPI(title="Aiko Analytics API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/stream/state")
def get_stream_state() -> dict:
    return _collector.snapshot()


@app.get("/api/revenue/summary")
def get_revenue_summary() -> dict:
    return {
        "total_today": _collector._donation_total,
        "donations_per_hour": _collector.donations_per_hour,
        "sources": {"donations": _collector._donation_total, "bits": 0, "subs": 0},
    }


@app.get("/api/viewers/top")
def get_top_viewers() -> dict:
    return {"top_donors": [], "top_chatters": []}


@app.get("/api/streams/history")
def get_stream_history() -> dict:
    return {"streams": []}


@app.get("/api/optimization/report")
def get_optimization_report() -> dict:
    return {"last_updated": None, "recommendations": [], "bandit_state": "not_initialized"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
