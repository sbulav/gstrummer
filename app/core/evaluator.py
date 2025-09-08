from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional
import threading


@dataclass
class StepResult:
    """Deviation of a user onset from the scheduled step."""

    step_index: int
    deviation_ms: float


class Evaluator:
    """Match detected onsets with scheduled steps and measure timing accuracy."""

    def __init__(self) -> None:
        self._onsets: Deque[float] = deque()
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Clear stored onsets."""
        with self._lock:
            self._onsets.clear()

    def add_onset(self, timestamp: float) -> None:
        """Record a detected onset timestamp (in seconds)."""
        with self._lock:
            self._onsets.append(timestamp)

    def add_step(self, step_index: int, timestamp: float) -> Optional[StepResult]:
        """Register a scheduled step and compare with the earliest onset.

        Args:
            step_index: Index of the scheduled step.
            timestamp: Timestamp of the scheduled step (seconds).

        Returns:
            StepResult with deviation in milliseconds if an onset was available,
            otherwise ``None``.
        """
        with self._lock:
            if not self._onsets:
                return None
            onset_ts = self._onsets.popleft()
        deviation_ms = (onset_ts - timestamp) * 1000.0
        return StepResult(step_index=step_index, deviation_ms=deviation_ms)
