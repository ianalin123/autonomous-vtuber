"""Clip agent — real-time moment detection and FFmpeg extraction."""
import time
from dataclasses import dataclass, field
from core.interfaces import EventType


@dataclass
class MomentDetector:
    chat_velocity_threshold: float = 30.0
    _velocity_history: list[float] = field(default_factory=list)
    _last_clip_time: float = 0.0

    def record_velocity(self, velocity: float) -> None:
        self._velocity_history.append(velocity)
        if len(self._velocity_history) > 10:
            self._velocity_history.pop(0)

    def is_clip_worthy(self, velocity: float) -> bool:
        if not self._velocity_history:
            return False
        avg = sum(self._velocity_history) / len(self._velocity_history)
        spike = velocity > avg * 2.5 and velocity > self.chat_velocity_threshold
        cooldown_ok = time.time() - self._last_clip_time > 120
        if spike and cooldown_ok:
            self._last_clip_time = time.time()
            return True
        return False
