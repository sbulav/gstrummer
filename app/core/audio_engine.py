import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from .chord_synth import generate_chord, render_soundfont_chord

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
except Exception as exc:  # pragma: no cover - optional dependency
    sd = None  # type: ignore[assignment]
    logger.warning("sounddevice not available: %s", exc)


@dataclass(eq=False)
class QueuedSample:
    data: np.ndarray
    pos: int
    volume: float


class AudioEngine:
    """Enhanced audio engine with sounddevice backend and sample support."""

    def __init__(self):
        self._sample_rate = 44100
        self._channels = 1  # Mono output
        self._dtype = np.float32
        self._buffer_size = 1024
        self._enabled = True

        # Optional UI error callback for display in GUI
        self._error_callback = None


        # Volume controls (0.0 to 1.0)
        self._click_volume = 0.7
        self._strum_volume = 0.5
        self._master_volume = 0.8

        # Enable/disable controls for different audio types
        self._click_enabled = True
        self._strum_enabled = True

        # Default instrument for generated chords
        self._chord_instrument = "guitar"

        # Default SoundFont path (can be customized by user)
        self._soundfont_path = str(
            Path(__file__).parent.parent.parent / "assets" / "soundfonts" / "acoustic_guitar.sf2"
        )

        # Sample cache - keeping the original format for backward compatibility but also supporting tuple format
        self._samples: Dict[str, np.ndarray] = {}

        # Streaming output for persistent stream approach (if sounddevice available)
        self._stream: Optional[Any] = None
        self._active_samples: List[QueuedSample] = []

        # Audio device info
        self._device_info: Optional[Any] = None
        self._audio_available = False

        # Thread safety
        self._audio_lock = threading.Lock()

        # Initialize audio system
        self._initialize_audio()
        if self._audio_available:
            self._load_samples()

    def _initialize_audio(self) -> None:
        """Initialize sounddevice with error handling and optional persistent stream."""
        if sd is None:
            logger.warning("sounddevice module not available, audio disabled")
            self._audio_available = False
            return

        try:
            # Get default output device
            self._device_info = sd.query_devices(kind="output")

            # Test audio output
            sd.check_output_settings(
                device=None,
                channels=self._channels,
                samplerate=self._sample_rate,
                dtype=self._dtype,
            )

            # Try to create persistent output stream with callback
            try:
                self._stream = sd.OutputStream(
                    samplerate=self._sample_rate,
                    channels=self._channels,
                    blocksize=self._buffer_size,
                    dtype=self._dtype,
                    callback=self._audio_callback,
                )
                self._stream.start()
                logger.info("Audio initialized with persistent stream")
            except Exception as stream_exc:
                logger.warning(
                    "Failed to create persistent stream, falling back to sd.play: %s",
                    stream_exc,
                )
                self._stream = None

            self._audio_available = True
            device_name = getattr(self._device_info, "name", str(self._device_info))
            logger.info("Audio initialized: %s", device_name)

        except Exception as e:
            logger.warning("Audio initialization failed: %s", e)
            self._audio_available = False

    def _load_samples(self):
        """Load audio samples in a background thread.

        The loader uses :func:`soundfile.read` when available and falls back to
        the built-in :mod:`wave` module. If a file is missing or cannot be
        decoded, a synthetic tone is generated instead. Loading happens
        asynchronously so the rest of the application can start before all
        samples are ready.
        """
        samples_dir = Path(__file__).parent.parent / "data" / "samples"

        sample_files = {
            "click_high": "clicks/click_high.wav",
            "click_low": "clicks/click_low.wav",
            "click_accent": "clicks/click_accent.wav",
            "strum_down": "strums/strum_down.wav",
            "strum_up": "strums/strum_up.wav",
            "strum_down_accent": "strums/strum_down_accent.wav",
            "strum_up_accent": "strums/strum_up_accent.wav",
        }

        def loader() -> None:
            for sample_name, file_path in sample_files.items():
                full_path = samples_dir / file_path
                if full_path.exists():
                    audio = self._read_file(full_path)
                    if audio is not None:
                        self._samples[sample_name] = audio
                        logger.info(f"Loaded sample: {sample_name}")
                        continue

                # Fallback if file missing or failed to decode
                self._samples[sample_name] = self._generate_sample(sample_name)
                logger.info(f"Generated fallback sample: {sample_name}")

        threading.Thread(target=loader, daemon=True).start()

    def _read_file(self, path: Path) -> Optional[np.ndarray]:
        """Decode a sound file using soundfile or wave.

        Returns ``None`` if decoding fails.
        """
        try:
            import soundfile as sf

            result = sf.read(str(path), dtype="float32", always_2d=False)
            data = result[0] if isinstance(result, tuple) else result  # type: ignore
            sr = result[1] if isinstance(result, tuple) and len(result) > 1 else self._sample_rate  # type: ignore
        except Exception:
            try:
                import wave

                with wave.open(str(path), "rb") as wf:
                    frames = wf.readframes(wf.getnframes())
                    dtype = np.int16 if wf.getsampwidth() == 2 else np.uint8
                    data = np.frombuffer(frames, dtype=dtype).astype(np.float32)
                    if wf.getnchannels() > 1:
                        data = data[:: wf.getnchannels()]
                    data /= 32768.0
                    sr = wf.getframerate()
            except Exception as exc:
                logger.warning(f"Could not decode {path}: {exc}")
                return None

        if sr != self._sample_rate:
            duration = len(data) / sr
            new_length = int(duration * self._sample_rate)
            data = np.interp(
                np.linspace(0, duration, new_length, endpoint=False),
                np.linspace(0, duration, len(data), endpoint=False),
                data,
            )

        return data.astype(self._dtype)

    def _generate_sample(self, sample_type: str) -> np.ndarray:
        """Generate synthetic audio samples as fallback."""
        duration = 0.1  # 100ms samples
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        if "click" in sample_type:
            if "high" in sample_type or "accent" in sample_type:
                # High click (800Hz sine wave with envelope)
                freq = 800
                amplitude = 0.3 if "accent" in sample_type else 0.2
            else:
                # Low click (400Hz sine wave)
                freq = 400
                amplitude = 0.15

            # Generate sine wave with exponential decay
            signal = amplitude * np.sin(2 * np.pi * freq * t)
            envelope = np.exp(-t * 20)  # Decay envelope
            sample = signal * envelope

        elif "strum" in sample_type:
            # Generate filtered noise for strum sounds
            noise = np.random.normal(0, 0.1, len(t))

            try:
                from scipy import signal as scipy_signal

                if "down" in sample_type:
                    # Downstroke: lower frequency emphasis
                    b, a = scipy_signal.butter(4, 800, "low", fs=self._sample_rate)
                    sample = scipy_signal.filtfilt(b, a, noise)
                else:
                    # Upstroke: higher frequency emphasis
                    b, a = scipy_signal.butter(4, 1200, "high", fs=self._sample_rate)
                    sample = scipy_signal.filtfilt(b, a, noise)
            except ImportError:
                # Fallback without scipy filtering
                if "down" in sample_type:
                    sample = noise * 0.8  # Slightly quieter for down
                else:
                    sample = noise * 1.2  # Slightly brighter for up

            # Apply envelope
            envelope = np.exp(-t * 5)
            amplitude = 0.2 if "accent" in sample_type else 0.1
            sample = sample * envelope * amplitude

        else:
            # Default: simple tone
            sample = 0.1 * np.sin(2 * np.pi * 440 * t) * np.exp(-t * 10)

        return sample.astype(self._dtype)

    def _audio_callback(
        self, outdata: np.ndarray, frames: int, callback_time: Any, status: Any
    ) -> None:
        """Mix active samples into the output buffer (used with persistent stream)."""
        if status:
            logger.warning("Audio callback status: %s", status)

        outdata.fill(0)

        with self._audio_lock:
            if not self._active_samples:
                return

            finished: List[QueuedSample] = []
            for sample in self._active_samples:
                start = sample.pos
                end = min(start + frames, sample.data.shape[0])
                chunk = sample.data[start:end]
                outdata[: end - start, 0] += chunk * sample.volume * self._master_volume
                sample.pos = end
                if sample.pos >= sample.data.shape[0]:
                    finished.append(sample)

            for sample in finished:
                self._active_samples.remove(sample)

    def _play_sample(self, sample_name: str, volume_multiplier: float = 1.0):
        """Play a sample with volume control."""
        if not self._enabled or not self._audio_available or sd is None:
            return

        if sample_name not in self._samples:
            logger.warning(
                f"Sample not loaded: {sample_name}, using generated fallback"
            )
            self._samples[sample_name] = self._generate_sample(sample_name)

        # If we have a persistent stream, use the callback approach
        if self._stream is not None:
            try:
                data = self._samples[sample_name].copy()
                data = np.asarray(data, dtype=self._dtype)

                with self._audio_lock:
                    self._active_samples.append(
                        QueuedSample(data=data, pos=0, volume=volume_multiplier)
                    )
                return
            except Exception as e:
                logger.warning(f"Stream playback failed for {sample_name}: {e}")
                # Fall through to sd.play approach

        # Fallback to sd.play approach
        try:
            with self._audio_lock:
                sample = self._samples[sample_name].copy()

                # Apply volume
                final_volume = self._master_volume * volume_multiplier
                sample *= final_volume

                # Play sample (non-blocking)
                sd.play(sample, samplerate=self._sample_rate, blocking=False)

        except Exception as e:
            logger.error(f"Error playing sample {sample_name}: {e}")

    def _play_data(self, data: np.ndarray, volume_multiplier: float = 1.0) -> None:
        """Play raw audio data with volume control."""
        if not self._enabled or not self._audio_available or sd is None:
            return

        # If we have a persistent stream, queue the data
        if self._stream is not None:
            try:
                arr = np.asarray(data, dtype=self._dtype)
                with self._audio_lock:
                    self._active_samples.append(
                        QueuedSample(data=arr, pos=0, volume=volume_multiplier)
                    )
                return
            except Exception as e:
                logger.warning(f"Stream playback failed: {e}")

        # Fallback to direct playback
        try:
            with self._audio_lock:
                arr = np.asarray(data, dtype=self._dtype)
                arr *= self._master_volume * volume_multiplier
                sd.play(arr, samplerate=self._sample_rate, blocking=False)
        except Exception as e:
            logger.error(f"Error playing generated audio: {e}")

    def play_click(self, accent: bool = False):
        """Play metronome click sound."""
        if not self._click_enabled:
            return

        if accent:
            sample_name = "click_accent"
            volume = self._click_volume * 1.2  # Boost accent volume
        else:
            sample_name = "click_low"
            volume = self._click_volume

        self._play_sample(sample_name, volume)

    def play_click_high(self):
        """Play high click for downbeat."""
        if not self._click_enabled:
            return
        self._play_sample("click_high", self._click_volume * 1.1)

    def play_strum(
        self,
        direction: str,
        accent: float = 0.0,
        technique: str = "open",
        chord: Optional[str] = None,
        instrument: Optional[str] = None,
    ) -> None:
        """Play strum sound or generated chord based on direction."""
        if direction == "-":
            return

        if chord:
            # Currently technique does not affect generated chords
            self.play_chord(
                chord,
                direction=direction,
                accent=accent,
                instrument=instrument,
            )
            return

        if not self._strum_enabled:
            return

        # Determine sample name - map single letters to full words
        direction_map = {"D": "down", "U": "up"}
        direction_word = direction_map.get(direction, direction.lower())

        if accent > 0.5:
            sample_name = f"strum_{direction_word}_accent"
        else:
            sample_name = f"strum_{direction_word}"

        # Calculate volume based on accent and technique
        base_volume = self._strum_volume
        accent_boost = accent * 0.3  # Up to 30% volume boost for accents

        technique_modifier = {
            "open": 1.0,
            "mute": 0.2,
            "palm": 0.5,
            "ghost": 0.3,
        }.get(technique, 1.0)

        volume = base_volume * (1.0 + accent_boost) * technique_modifier

        self._play_sample(sample_name, volume)

    def play_chord(
        self,
        chord: str,
        direction: str = "D",
        accent: float = 0.0,
        instrument: Optional[str] = None,
        duration: float = 1.0,
    ) -> None:
        """Generate and play a chord for songs mode."""
        if not self._strum_enabled:
            return

        chosen_instrument = instrument or self._chord_instrument
        soundfont_path = self._soundfont_path if chosen_instrument == "sf2_guitar" else None

        logger.debug("Playing chord %s with instrument %s (soundfont: %s)", 
                   chord, chosen_instrument, "Yes" if soundfont_path else "No")

        try:
            data = generate_chord(
                chord,
                instrument=chosen_instrument,
                direction=direction,
                duration=duration,
                sample_rate=self._sample_rate,
                soundfont_path=soundfont_path
            )
        except Exception as exc:
            logger.warning("Failed to generate chord %s: %s", chord, exc)
            if self._error_callback is not None:
                self._error_callback(f"Failed to generate chord '{chord}': {exc}")
            return

        base_volume = self._strum_volume
        accent_boost = accent * 0.3
        volume = base_volume * (1.0 + accent_boost)
        self._play_data(data, volume)

    def set_chord_instrument(self, instrument: str) -> None:
        """Set default instrument for generated chords."""
        logger.debug("Setting chord instrument to: %s", instrument)
        self._chord_instrument = instrument

    def get_chord_instrument(self) -> str:
        """Get current default chord instrument."""
        return self._chord_instrument

    def get_soundfont_path(self) -> str:
        """Get the path to the current SoundFont file."""
        return self._soundfont_path

    def set_soundfont_path(self, path: str) -> None:
        """Set the path to the SoundFont (.sf2) file used for sf2_guitar."""
        self._soundfont_path = path

    def set_error_callback(self, cb):
        """Set a callback (callable) to be invoked on chord/audio errors."""
        self._error_callback = cb

    def get_available_instruments(self) -> List[str]:
        """Return list of available chord instruments."""
        instruments = ["guitar"]
        if render_soundfont_chord is not None:
            instruments.append("sf2_guitar")
        return instruments

    def set_volumes(
        self,
        click: Optional[float] = None,
        strum: Optional[float] = None,
        master: Optional[float] = None,
    ):
        """Set volume levels (0.0 to 1.0)."""
        with self._audio_lock:
            if click is not None:
                self._click_volume = max(0.0, min(1.0, click))
            if strum is not None:
                self._strum_volume = max(0.0, min(1.0, strum))
            if master is not None:
                self._master_volume = max(0.0, min(1.0, master))

    def get_volumes(self) -> Dict[str, float]:
        """Get current volume levels."""
        return {
            "click": self._click_volume,
            "strum": self._strum_volume,
            "master": self._master_volume,
        }

    def set_click_enabled(self, enabled: bool):
        """Enable or disable metronome click sounds."""
        self._click_enabled = enabled

    def set_strum_enabled(self, enabled: bool):
        """Enable or disable strum sounds."""
        self._strum_enabled = enabled

    def is_click_enabled(self) -> bool:
        """Check if metronome clicks are enabled."""
        return self._click_enabled

    def is_strum_enabled(self) -> bool:
        """Check if strum sounds are enabled."""
        return self._strum_enabled

    def set_enabled(self, enabled: bool):
        """Enable or disable audio playback."""
        self._enabled = enabled

    def is_available(self) -> bool:
        """Check if audio system is available."""
        return self._audio_available

    def get_device_info(self) -> Optional[Any]:
        """Get current audio device information."""
        return self._device_info

    def stop_all(self):
        """Stop all currently playing sounds."""
        if not self._audio_available or sd is None:
            return

        # Clear active samples if using persistent stream
        if self._stream is not None:
            with self._audio_lock:
                self._active_samples.clear()
            # Restart stream to clear any pending audio
            try:
                self._stream.stop()
                self._stream.start()
            except Exception as e:
                logger.warning(f"Failed to restart stream: {e}")
        else:
            # Use sd.stop for non-persistent approach
            sd.stop()

    def close(self):
        """Clean shutdown of audio system."""
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")
        elif sd is not None and hasattr(sd, "get_stream") and sd.get_stream():
            try:
                sd.get_stream().close()
            except Exception as e:
                logger.warning(f"Error closing sounddevice stream: {e}")
