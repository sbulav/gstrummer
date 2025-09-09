import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.chord_synth import generate_chord


def test_generate_chord_guitar():
    data = generate_chord("Am", instrument="guitar", duration=0.2, sample_rate=8000)
    assert isinstance(data, np.ndarray)
    assert data.dtype == np.float32
    assert data.size == int(0.2 * 8000)
    assert np.any(data != 0)


def test_generate_chord_piano():
    data = generate_chord("C", instrument="piano", duration=0.2, sample_rate=8000)
    assert isinstance(data, np.ndarray)
    assert data.dtype == np.float32
    assert data.size == int(0.2 * 8000)
    assert np.any(data != 0)


def test_generate_chord_soundfont():
    pytest.importorskip("fluidsynth")
    sf_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "soundfonts", "acoustic_guitar.sf2"
    )
    if not os.path.exists(sf_path):
        pytest.skip("soundfont file not available")
    data = generate_chord("Am", instrument="sf2_guitar", duration=0.2, sample_rate=8000)
    assert isinstance(data, np.ndarray)
    assert data.dtype == np.float32
    assert data.size == int(0.2 * 8000)
    assert np.any(data != 0)
