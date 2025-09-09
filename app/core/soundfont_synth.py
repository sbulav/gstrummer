"""SoundFont-based chord synthesizer."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np

from .chord_library import get_chord_diagram

try:
    import fluidsynth
except Exception:  # pragma: no cover - optional dependency
    fluidsynth = None  # type: ignore[assignment]

# MIDI numbers for standard tuning strings E2..E4
BASE_MIDI = [40, 45, 50, 55, 59, 64]


def _midi_notes_from_chord(chord_name: str) -> list[int]:
    """Return MIDI notes for strings in chord diagram."""
    diagram = get_chord_diagram(chord_name)
    if diagram is None:
        raise ValueError(f"Unknown chord: {chord_name}")
    notes: list[int] = []
    for base, fret in zip(BASE_MIDI, diagram.frets):
        if fret < 0:
            continue
        notes.append(base + fret)
    return notes


def render_chord(
    chord_name: str,
    direction: str = "D",
    duration: float = 1.0,
    sample_rate: int = 44100,
    soundfont_path: str | None = None,
) -> np.ndarray:
    """Render a chord using a SoundFont guitar timbre.

    Parameters
    ----------
    chord_name:
        Name of the chord (e.g., ``"Am"``).
    direction:
        ``"D"`` for down strum or ``"U"`` for up strum.
    duration:
        Length of resulting audio in seconds.
    sample_rate:
        Output sample rate.
    soundfont_path:
        Optional path to a SoundFont (SF2). If omitted, uses
        ``assets/soundfonts/acoustic_guitar.sf2``.
    """
    if fluidsynth is None:
        raise RuntimeError("pyfluidsynth not available")

    if soundfont_path is None:
        soundfont_path = (
            Path(__file__).resolve().parent.parent
            / ".."
            / "assets"
            / "soundfonts"
            / "acoustic_guitar.sf2"
        )
    sf_path = Path(soundfont_path)
    if not sf_path.exists():
        raise FileNotFoundError(f"SoundFont not found: {sf_path}")

    notes = _midi_notes_from_chord(chord_name)
    if not notes:
        return np.zeros(int(sample_rate * duration), dtype=np.float32)

    synth = fluidsynth.Synth(samplerate=sample_rate)
    sfid = synth.sfload(str(sf_path))
    synth.program_select(0, sfid, 0, 0)

    total_samples = int(sample_rate * duration)
    buffer = np.zeros(total_samples, dtype=np.float32)
    strum_delay = 0.012  # 12 ms between strings

    # Start first note immediately
    order: Iterable[int] = notes if direction.upper() == "D" else reversed(notes)
    iterator = iter(order)
    try:
        first_note = next(iterator)
    except StopIteration:
        return buffer
    synth.noteon(0, first_note, 100)

    current_pos = 0
    delay_samples = int(strum_delay * sample_rate)
    for note in iterator:
        # advance time before next note
        samples = np.array(synth.get_samples(delay_samples), dtype=np.float32)
        end_pos = current_pos + delay_samples
        buffer[current_pos:end_pos] += samples[:delay_samples]
        current_pos = end_pos
        synth.noteon(0, note, 100)

    # render remaining samples
    remaining = total_samples - current_pos
    if remaining > 0:
        samples = np.array(synth.get_samples(remaining), dtype=np.float32)
        buffer[current_pos:] += samples[:remaining]

    synth.delete()
    return buffer


__all__ = ["render_chord"]
