import numpy as np
from app.core.audio_engine import AudioEngine


def test_audio_engine_instrument_switch(monkeypatch):
    engine = AudioEngine()
    called = {}

    def fake_generate_chord(chord, instrument, direction, duration, sample_rate):
        called["instrument"] = instrument
        return np.zeros(int(sample_rate * duration), dtype=np.float32)

    monkeypatch.setattr("app.core.audio_engine.generate_chord", fake_generate_chord)

    engine.set_chord_instrument("guitar")
    engine.play_strum("D", chord="Am")
    assert called["instrument"] == "guitar"

    if "sf2_guitar" in engine.get_available_instruments():
        engine.set_chord_instrument("sf2_guitar")
        engine.play_strum("D", chord="Am")
        assert called["instrument"] == "sf2_guitar"
