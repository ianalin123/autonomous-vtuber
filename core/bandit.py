"""Thompson Sampling contextual bandit for engagement-revenue optimization."""
from __future__ import annotations
import random
from enum import Enum


class Action(str, Enum):
    TALK = "talk"
    REACT = "react"
    GAME = "game"
    QA = "q_and_a"
    IDLE = "idle"


class ThompsonBandit:
    """Beta-Bernoulli Thompson Sampling bandit.

    Each arm tracks alpha (successes) and beta (failures).
    Reward signal: normalized donation rate + engagement score delta.
    """

    def __init__(self, actions: list[Action]) -> None:
        self._arms: dict[Action, dict[str, float]] = {
            action: {"alpha": 1.0, "beta": 1.0} for action in actions
        }

    def select(self) -> Action:
        """Sample from each arm's Beta distribution, pick the max."""
        samples = {
            action: random.betavariate(arm["alpha"], arm["beta"])
            for action, arm in self._arms.items()
        }
        return max(samples, key=lambda a: samples[a])

    def exploit(self) -> Action:
        """Greedy: pick arm with highest expected value (alpha / (alpha + beta))."""
        return max(
            self._arms,
            key=lambda a: self._arms[a]["alpha"] / (self._arms[a]["alpha"] + self._arms[a]["beta"]),
        )

    def update(self, action: Action, reward: float) -> None:
        """Update arm with observed reward (0.0-1.0 normalized)."""
        if action not in self._arms:
            return
        if reward > 0:
            self._arms[action]["alpha"] += reward
        else:
            self._arms[action]["beta"] += 1.0

    def state(self) -> dict:
        return {
            action.value: {
                "alpha": round(arm["alpha"], 3),
                "beta": round(arm["beta"], 3),
                "expected": round(arm["alpha"] / (arm["alpha"] + arm["beta"]), 3),
            }
            for action, arm in self._arms.items()
        }
