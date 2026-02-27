"""Subscriber retention tracker with tenure-aware appreciation."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class SubscriberTracker:
    db: object  # Neo4jDB | None
    _subs: dict[str, dict] = field(default_factory=dict)

    def add(self, username: str, tier: int = 1) -> None:
        self._subs[username] = {"tier": tier, "months": 1}
        if self.db:
            self.db.upsert_viewer(username, sub_tier=tier)

    def renew(self, username: str) -> None:
        if username in self._subs:
            self._subs[username]["months"] += 1
            if self.db:
                self.db.upsert_viewer(username, sub_tier=self._subs[username]["tier"])

    def churn(self, username: str) -> None:
        self._subs.pop(username, None)

    def is_subscriber(self, username: str) -> bool:
        return username in self._subs

    @property
    def sub_count(self) -> int:
        return len(self._subs)

    def tier_breakdown(self) -> dict[int, int]:
        counts: dict[int, int] = defaultdict(int)
        for sub in self._subs.values():
            counts[sub["tier"]] += 1
        return dict(counts)

    def format_sub_appreciation(self, username: str) -> str:
        if username not in self._subs:
            return f"{username} thanks for being here!"
        months = self._subs[username]["months"]
        tier = self._subs[username]["tier"]
        if months >= 12:
            return f"{username} has been here for {months} months?? {username} you are LITERALLY part of the family I hope you know that"
        if months >= 6:
            return f"okay {username} has been subbed for {months} months — {username} thank you for sticking around you mean so much"
        if tier >= 3:
            return f"TIER THREE {username}!! {username} you are too good to me I cannot"
        return f"{username} thank you for the sub!! welcome to the chaos, we're so glad you're here"
