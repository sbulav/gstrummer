import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from guitar_trainer import GuitarTrainer
from app.core.patterns import Step, StrumPattern

try:  # pragma: no cover - environment may lack Qt libs
    from app.ui.practice_view import PracticeView
except Exception:  # pragma: no cover
    PracticeView = None


class DummyAudio:
    def __init__(self):
        self.calls = []

    def play_strum(self, direction, accent, technique, chord=None):
        self.calls.append((direction, accent, technique, chord))

    def play_click(self, accent=False):
        pass

    def play_click_high(self):
        pass


class DummyMetronome:
    def __init__(self, bpm=120):
        self.bpm = bpm
        self.durations: list[float] = []

    def set_step_duration(self, duration: float):
        self.durations.append(duration)


class DummyVisualizer:
    def draw_timeline(self, pattern, step_index, bpm, chord):
        pass


pattern = StrumPattern(
    id="uneven",
    name="Uneven",
    time_sig=(4, 4),
    steps_per_bar=4,
    steps=[
        Step(0.0, "D", 1.0),
        Step(0.2, "U"),
        Step(0.5, "D"),
        Step(0.6, "U"),
    ],
    bpm_default=120,
    bpm_min=60,
    bpm_max=180,
    notes="",
)

expected_durations = [0.4, 0.6, 0.2, 0.8]


@pytest.mark.skipif(PracticeView is None, reason="PracticeView import failed")
def test_practice_view_uneven_timing():
    view = PracticeView.__new__(PracticeView)
    view.audio = DummyAudio()
    view.metronome = DummyMetronome(bpm=120)
    view.current_pattern = pattern
    view.current_progression = []
    view.current_chord_index = 0

    for idx, expected in enumerate(expected_durations):
        view.on_practice_tick(0.0, idx)
        assert view.metronome.durations[-1] == pytest.approx(expected)
    assert len(view.audio.calls) == 4


def test_guitar_trainer_uneven_timing():
    trainer = GuitarTrainer.__new__(GuitarTrainer)
    trainer.audio = DummyAudio()
    trainer.metronome = DummyMetronome(bpm=120)
    trainer.visualizer = DummyVisualizer()
    trainer.current_pattern = pattern
    trainer.current_song = None

    for idx, expected in enumerate(expected_durations):
        trainer.on_tick(0.0, idx)
        assert trainer.metronome.durations[-1] == pytest.approx(expected)
    assert len(trainer.audio.calls) == 4
