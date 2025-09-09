"""SoundFont-based chord synthesizer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import numpy as np

from .chord_library import get_chord_diagram

logger = logging.getLogger(__name__)

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
        Optional path to a SoundFont (SF2) file. If omitted, uses
        ``assets/soundfonts/acoustic_guitar.sf2``.
    """
    if fluidsynth is None:
        raise RuntimeError("pyfluidsynth not available (required for SoundFont synthesis)")

    # Set default soundfont path
    if soundfont_path is None:
        soundfont_path = str(
            Path(__file__).resolve().parent.parent.parent / "assets" / "soundfonts" / "acoustic_guitar.sf2"
        )
    # Always cast to string (in case some caller gave us a Path)
    sf_path = Path(str(soundfont_path))
    if not sf_path.exists():
        raise FileNotFoundError(f"SoundFont not found: {sf_path}")

    notes = _midi_notes_from_chord(chord_name)
    if not notes:
        return np.zeros(int(sample_rate * duration), dtype=np.float32)

    synth = fluidsynth.Synth(samplerate=sample_rate)
    sfid = synth.sfload(str(sf_path))
    
    def _try_find_any_preset(synth, sfid):
        """Try to find any working preset in the SoundFont."""
        # Try common banks and presets
        for bank in [0, 128]:
            for preset in range(128):  # Try all presets in the bank
                try:
                    synth.program_select(0, sfid, bank, preset)
                    logger.debug("Found working preset: bank %s, preset %s", bank, preset)
                    return True
                except Exception:
                    continue
        
        # If that fails, try bank -1 (sometimes used)
        try:
            synth.program_select(0, sfid, -1, 0)
            logger.debug("Using bank -1, preset 0")
            return True
        except Exception:
            pass
        
        return False
    
    # Try common guitar presets - bank 0, preset 24-31 are often guitars
    # If that fails, try bank 128 (percussion) or scan for available presets
    guitar_presets = [
        (0, 24),  # Acoustic Guitar (nylon)
        (0, 25),  # Acoustic Guitar (steel)
        (0, 26),  # Electric Guitar (jazz)
        (0, 27),  # Electric Guitar (clean)
        (0, 28),  # Electric Guitar (muted)
        (0, 29),  # Overdriven Guitar
        (0, 30),  # Distortion Guitar
        (0, 31),  # Guitar harmonics
        (128, 0), # Sometimes guitars are in percussion bank
    ]
    
    # Try each preset until we find one that works
    preset_found = False
    for bank, preset in guitar_presets:
        try:
            synth.program_select(0, sfid, bank, preset)
            logger.debug("Using SoundFont preset: bank %s, preset %s", bank, preset)
            preset_found = True
            break
        except Exception:
            continue
    
    if not preset_found:
        # Scan for any available preset if standard ones don't work
        logger.warning("No standard guitar preset found, scanning SoundFont")
        preset_found = _try_find_any_preset(synth, sfid)
        
    if not preset_found:
        logger.error("Could not select any preset in SoundFont")
        return np.zeros(int(sample_rate * duration), dtype=np.float32)

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
    
    # Use reduced velocity to prevent clipping (70 instead of 100)
    velocity = 70
    synth.noteon(0, first_note, velocity)

    current_pos = 0
    delay_samples = int(strum_delay * sample_rate)
    for note in iterator:
        # advance time before next note
        samples = np.array(synth.get_samples(delay_samples), dtype=np.float32)
        end_pos = current_pos + delay_samples
        buffer[current_pos:end_pos] += samples[:delay_samples]
        current_pos = end_pos
        synth.noteon(0, note, velocity)

    # render remaining samples
    remaining = total_samples - current_pos
    if remaining > 0:
        samples = np.array(synth.get_samples(remaining), dtype=np.float32)
        buffer[current_pos:] += samples[:remaining]

    synth.delete()
    
    # Apply additional volume scaling for SoundFonts that are too loud
    max_val = np.max(np.abs(buffer))
    if max_val > 0.5:  # If the sound is too loud
        scale_factor = 0.5 / max_val  # Scale to max 0.5 amplitude
        buffer = buffer * scale_factor
    
    return buffer


def _try_find_any_preset(synth, sfid):
    """Try to find any working preset in the SoundFont."""
    # Try common banks and presets
    for bank in [0, 128]:
        for preset in range(128):  # Try all presets in the bank
            try:
                synth.program_select(0, sfid, bank, preset)
                logger.debug("Found working preset: bank %s, preset %s", bank, preset)
                return True
            except Exception:
                continue
    
    # If that fails, try bank -1 (sometimes used)
    try:
        synth.program_select(0, sfid, -1, 0)
        logger.debug("Using bank -1, preset 0")
        return True
    except Exception:
        pass
    
    return False


__all__ = ["render_chord"]
