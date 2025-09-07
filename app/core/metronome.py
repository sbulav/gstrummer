import time
import threading
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal, QTimer


class Metronome(QObject):
    """Enhanced metronome with Qt signal integration for GUI updates."""
    
    # Qt signals for thread-safe communication with GUI
    tick = Signal(float, int)  # timestamp, step_index
    started = Signal()
    stopped = Signal()
    bpm_changed = Signal(int)
    
    def __init__(self, bpm: int = 120, steps_per_beat: int = 2):
        super().__init__()
        self.bpm = bpm
        self.steps_per_beat = steps_per_beat
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Callable[[float, int], None] = lambda ts, idx: None
        self._current_step = 0
        
        # Connect internal signal to callback for backward compatibility
        self.tick.connect(self._on_tick)

    def set_bpm(self, bpm: int):
        """Set BPM with bounds checking."""
        new_bpm = max(30, min(300, bpm))
        if new_bpm != self.bpm:
            self.bpm = new_bpm
            self.bpm_changed.emit(self.bpm)

    def set_callback(self, callback: Callable[[float, int], None]):
        """Set callback for backward compatibility."""
        self._callback = callback
        
    def _on_tick(self, timestamp: float, step_index: int):
        """Internal tick handler that calls the callback."""
        self._callback(timestamp, step_index)

    def _run(self):
        """Main metronome thread loop with improved timing accuracy."""
        step_duration = 60.0 / self.bpm / self.steps_per_beat
        next_time = time.perf_counter()
        last_bpm = self.bpm
        
        while self._running:
            current_time = time.perf_counter()
            
            # Check if BPM changed and recalculate timing
            if self.bpm != last_bpm:
                step_duration = 60.0 / self.bpm / self.steps_per_beat
                last_bpm = self.bpm
                # Adjust next_time to maintain phase
                next_time = current_time + step_duration
            
            if current_time >= next_time:
                # Emit Qt signal for GUI updates (thread-safe)
                self.tick.emit(current_time, self._current_step)
                self._current_step += 1
                next_time += step_duration
            
            # Adaptive sleep for better timing precision
            sleep_time = max(0, next_time - time.perf_counter() - 0.001)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def start(self):
        """Start the metronome."""
        if self._running:
            return
        
        self._running = True
        self._current_step = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.started.emit()

    def stop(self):
        """Stop the metronome."""
        if not self._running:
            return
            
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        self.stopped.emit()

    def pause(self):
        """Pause the metronome (alias for stop)."""
        self.stop()
        
    def reset(self):
        """Reset step counter to zero."""
        self._current_step = 0

    def is_running(self) -> bool:
        """Check if metronome is currently running."""
        return self._running
        
    def get_current_step(self) -> int:
        """Get the current step index."""
        return self._current_step