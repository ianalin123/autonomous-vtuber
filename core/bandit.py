"""Thompson Sampling contextual bandit for engagement-revenue optimization."""
from __future__ import annotations
import json
import random
from enum import Enum
from pathlib import Path


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

    def save(self, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.state(), indent=2))

    @classmethod
    def load(cls, path: str) -> ThompsonBandit:
        data = json.loads(Path(path).read_text())
        actions = [Action(name) for name in data]
        bandit = cls(actions)
        for name, arm_data in data.items():
            action = Action(name)
            bandit._arms[action]["alpha"] = arm_data["alpha"]
            bandit._arms[action]["beta"] = arm_data["beta"]
        return bandit

    @classmethod
    def load_or_create(cls, path: str) -> ThompsonBandit:
        try:
            return cls.load(path)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return cls(list(Action))
