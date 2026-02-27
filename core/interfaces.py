"""Shared event and message contracts — all agents import from here."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    CHAT_MESSAGE = "chat_message"
    DONATION = "donation"
    SUBSCRIPTION = "subscription"
    RAID = "raid"
    VIEWER_COUNT = "viewer_count"
    SPEAK = "speak"
    SET_EXPRESSION = "set_expression"
    CLIP_MOMENT = "clip_moment"
    STREAM_STATE = "stream_state"


@dataclass
class Event:
    type: EventType
    payload: dict[str, Any]
    priority: int = 0
    source: str = "unknown"


@dataclass
class ChatMessage:
    username: str
    text: str
    is_donation: bool = False
    donation_amount: float = 0.0
    is_sub: bool = False
    sub_tier: int = 0
    badges: list[str] = field(default_factory=list)


@dataclass
class StreamState:
    viewer_count: int = 0
    chat_velocity: float = 0.0
    donations_per_hour: float = 0.0
    current_activity: str = "idle"
    engagement_score: float = 0.0
