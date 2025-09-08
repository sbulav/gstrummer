import time
import threading
from app.core.metronome import Metronome


def test_metronome_yields_cpu_and_timing():
    met = Metronome(bpm=600, steps_per_beat=2)
    timestamps = []
    done = threading.Event()

    def callback(ts: float, idx: int) -> None:
        timestamps.append(ts)
        if len(timestamps) >= 5:
            done.set()

    met.set_callback(callback)

    # Bypass Qt signal delivery by replacing the signal with a lightweight
    # object that calls the callback immediately. This keeps the thread loop
    # intact while avoiding the need for a Qt event loop in tests.
    class _DummySignal:
        def __init__(self, cb):
            self._cb = cb

        def emit(self, ts, idx):  # type: ignore[override]
            self._cb(ts, idx)

    met.tick = _DummySignal(met._on_tick)  # type: ignore[assignment]

    start_cpu = time.process_time()
    start_wall = time.perf_counter()

    met.start()
    assert done.wait(2), "Metronome did not emit ticks in time"
    met.stop()

    cpu_time = time.process_time() - start_cpu
    wall_time = time.perf_counter() - start_wall
    assert cpu_time / wall_time < 0.8

    expected = 60.0 / 600 / 2
    intervals = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
    for interval in intervals:
        assert abs(interval - expected) < 0.015
