"""Donation goal tracker with milestone announcements."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

MILESTONE_PCTS = [25, 50, 75, 100]


@dataclass
class Goal:
    target: float
    description: str


class DonationGoalTracker:
    def __init__(self) -> None:
        self._goal: Goal | None = None
        self.current_total: float = 0.0
        self._triggered: set[int] = set()
        self.on_milestone: Callable[[int, str], None] = lambda pct, msg: None
        self.on_complete: Callable[[str], None] = lambda msg: None

    def set_goal(self, goal: Goal) -> None:
        self._goal = goal
        self.current_total = 0.0
        self._triggered.clear()

    @property
    def progress_pct(self) -> float:
        if not self._goal or self._goal.target == 0:
            return 0.0
        return round((self.current_total / self._goal.target) * 100, 1)

    def record_donation(self, amount: float) -> None:
        if not self._goal:
            return
        self.current_total += amount
        pct = self.progress_pct
        for milestone in MILESTONE_PCTS:
            if pct >= milestone and milestone not in self._triggered:
                self._triggered.add(milestone)
                if milestone == 100:
                    msg = f"WE HIT THE GOAL — {self._goal.description}!! THANK YOU CHAT"
                    self.on_complete(msg)
                else:
                    msg = f"chat we're at {milestone}% of the goal — {self.announce_text()}"
                    self.on_milestone(milestone, msg)

    def announce_text(self) -> str:
        if not self._goal:
            return ""
        remaining = max(0.0, self._goal.target - self.current_total)
        return (
            f"we're at ${self.current_total:.2f} of ${self._goal.target:.2f} — "
            f"only ${remaining:.2f} left! {self._goal.description}"
        )
