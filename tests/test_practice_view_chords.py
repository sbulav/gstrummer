from app.ui.practice_view import PracticeView
from app.core.patterns import Step, StrumPattern


class DummyAudio:
    def __init__(self):
        self.calls = []

    def play_strum(self, direction, accent, technique, chord=None):
        self.calls.append((direction, accent, technique, chord))

    def play_click_high(self):
        pass

    def play_click(self, accent=False):
        pass


def test_on_practice_tick_uses_current_chord():
    view = PracticeView.__new__(PracticeView)
    view.audio = DummyAudio()
    view.current_progression = ["Am", "E"]
    view.current_chord_index = 0
    view.current_pattern = StrumPattern(
        id="test",
        name="Test",
        time_sig=(4, 4),
        steps_per_bar=4,
        steps=[Step(0.0, "D", 1.0)],
        bpm_default=120,
        bpm_min=60,
        bpm_max=180,
        notes="",
    )

    view.on_practice_tick(0.0, 0)

    assert view.audio.calls == [("D", 1.0, "open", "Am")]
