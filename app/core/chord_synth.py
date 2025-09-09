"""Simple chord synthesizer for guitar and piano sounds."""

from __future__ import annotations

import numpy as np

from .chord_library import get_chord_diagram

try:
    from .soundfont_synth import render_chord as render_soundfont_chord
except Exception:  # pragma: no cover - optional dependency
    render_soundfont_chord = None  # type: ignore[assignment]

# Standard tuning for guitar (E2, A2, D3, G3, B3, E4)
STANDARD_TUNING = [82.41, 110.0, 146.83, 196.0, 246.94, 329.63]


def _frequencies_from_chord(chord_name: str) -> list[float]:
    """Get frequencies for all strings in a chord diagram."""
    diagram = get_chord_diagram(chord_name)
    if diagram is None:
        raise ValueError(f"Unknown chord: {chord_name}")
    freqs: list[float] = []
    for base, fret in zip(STANDARD_TUNING, diagram.frets):
        if fret < 0:
            continue  # muted string
        freqs.append(base * (2 ** (fret / 12)))
    return freqs


def generate_chord(
    chord_name: str,
    instrument: str = "guitar",
    direction: str = "D",
    duration: float = 1.0,
    sample_rate: int = 44100,
) -> np.ndarray:
    """Generate a chord waveform.

    Parameters
    ----------
    chord_name:
        Name of the chord (e.g., "Am", "C").
    instrument:
        ``"guitar"``, ``"piano"`` or ``"sf2_guitar"``.
    direction:
        Strum direction, ``"D"`` or ``"U"``. Used for guitar to stagger note
        start times.
    duration:
        Duration of generated sound in seconds.
    sample_rate:
        Sampling rate of the generated waveform.
    """

    if instrument == "sf2_guitar":
        if render_soundfont_chord is None:
            raise RuntimeError("SoundFont backend not available")
        return render_soundfont_chord(
            chord_name,
            direction=direction,
            duration=duration,
            sample_rate=sample_rate,
        ).astype(np.float32)

    freqs = _frequencies_from_chord(chord_name)
    if not freqs:
        return np.zeros(int(sample_rate * duration), dtype=np.float32)

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    output = np.zeros_like(t)

    if instrument == "piano":
        envelope = np.exp(-3 * t)
        for f in freqs:
            wave = (
                np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t)
            ) * envelope
            output[: wave.size] += wave
    else:  # guitar
        strum_delay = 0.01  # seconds between strings
        indices = list(range(len(freqs)))
        if direction.upper() == "U":
            indices = list(reversed(indices))
        for i, idx in enumerate(indices):
            f = freqs[idx]
            delay_samples = int(i * strum_delay * sample_rate)
            segment = t[: t.size - delay_samples]
            env = np.exp(-5 * segment)
            wave = np.sin(2 * np.pi * f * segment) * env
            output[delay_samples : delay_samples + wave.size] += wave

    # Normalize amplitude
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / (max_val * len(freqs))

    return output.astype(np.float32)


__all__ = ["generate_chord"]
