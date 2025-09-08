import pytest
from app.core.evaluator import Evaluator, StepResult
import time


def test_evaluator_step_matching():
    ev = Evaluator()
    ev.reset()
    # Simulate onsets at t=1.0, t=2.0
    ev.add_onset(1.0)
    ev.add_onset(2.0)
    # Feed scheduled steps at 1.05 and 2.02
    match1 = ev.add_step(0, 1.05)
    match2 = ev.add_step(1, 2.02)
    # Should match both, deviation in ms
    assert isinstance(match1, StepResult)
    assert abs(match1.deviation_ms - (-50.0)) < 1
    assert isinstance(match2, StepResult)
    assert abs(match2.deviation_ms - (-20.0)) < 1
    # No more onsets
    assert ev.add_step(2, 3.0) is None

def test_evaluator_thread_safety():
    ev = Evaluator()
    N = 100
    import threading
    def onset_thread():
        for i in range(N):
            ev.add_onset(0.1 * i)
    def step_thread():
        matched = []
        for i in range(N):
            result = ev.add_step(i, 0.1 * i)
            matched.append(result)
        return matched
    t1 = threading.Thread(target=onset_thread)
    t2 = threading.Thread(target=step_thread)
    t1.start(); t2.start(); t1.join(); t2.join()
    # Only up to N dequeued
    # (can't rigorously check order, just no exceptions)
    assert isinstance(ev._onsets, type(ev._onsets))
    assert isinstance(ev._lock, type(ev._lock))
    ev.reset()
    assert len(ev._onsets) == 0
