import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
except Exception as exc:  # pragma: no cover - optional dependency
    sd = None  # type: ignore[assignment]
    logger.warning("sounddevice not available: %s", exc)


class AudioEngine:
    """Enhanced audio engine with sounddevice backend and sample support."""

    def __init__(self):
        self._sample_rate = 44100
        self._channels = 1  # Mono output
        self._dtype = np.float32
        self._buffer_size = 1024
        self._enabled = True

        # Volume controls (0.0 to 1.0)
        self._click_volume = 0.7
        self._strum_volume = 0.5
        self._master_volume = 0.8

        # Enable/disable controls for different audio types
        self._click_enabled = True
        self._strum_enabled = True

        # Sample cache
        self._samples: Dict[str, Tuple[np.ndarray, int]] = {}

        # Streaming output
        self._stream: Optional[Any] = None
        self._active_samples: List["QueuedSample"] = []

        # Audio device info
        self._device_info = None
        self._audio_available = False

        # Thread safety
        self._audio_lock = threading.Lock()

        # Initialize audio system
        self._initialize_audio()
        if self._audio_available:
            self._load_samples()

    def _initialize_audio(self) -> None:
        """Initialize sounddevice with a persistent output stream."""
        if sd is None:
            logger.warning("sounddevice module not available, audio disabled")
            self._audio_available = False
            return
        try:
            self._device_info = sd.query_devices(kind="output")
            sd.check_output_settings(
                device=None,
                channels=self._channels,
                samplerate=self._sample_rate,
                dtype=self._dtype,
            )
            self._stream = sd.OutputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                blocksize=self._buffer_size,
                dtype=self._dtype,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._audio_available = True
            logger.info("Audio initialized: %s", self._device_info["name"])
        except Exception as exc:
            logger.warning("Audio initialization failed: %s", exc)
            self._audio_available = False

    def _load_samples(self) -> None:
        """Load audio samples from files or generate fallback sounds."""
        samples_dir = Path(__file__).parent.parent / "data" / "samples"

        # Define sample files to load
        sample_files = {
            "click_high": "clicks/click_high.wav",
            "click_low": "clicks/click_low.wav",
            "click_accent": "clicks/click_accent.wav",
            "strum_down": "strums/strum_down.wav",
            "strum_up": "strums/strum_up.wav",
            "strum_down_accent": "strums/strum_down_accent.wav",
            "strum_up_accent": "strums/strum_up_accent.wav",
        }

        for sample_name, file_path in sample_files.items():
            full_path = samples_dir / file_path

            if full_path.exists():
                try:
                    # Load with librosa if available, otherwise use generated sounds
                    import librosa

                    audio, sr = librosa.load(
                        str(full_path), sr=self._sample_rate, mono=True
                    )
                    self._samples[sample_name] = (audio.astype(self._dtype), sr)
                    logger.info(f"Loaded sample: {sample_name}")

                except ImportError:
                    logger.warning("librosa not available, using generated sounds")
                    self._samples[sample_name] = (
                        self._generate_sample(sample_name),
                        self._sample_rate,
                    )
                except Exception as e:
                    logger.warning(f"Failed to load {sample_name}: {e}")
                    self._samples[sample_name] = (
                        self._generate_sample(sample_name),
                        self._sample_rate,
                    )
            else:
                # Generate fallback sound
                self._samples[sample_name] = (
                    self._generate_sample(sample_name),
                    self._sample_rate,
                )
                logger.info(f"Generated fallback sample: {sample_name}")

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
    ) -> None:  # type: ignore[override]
        """Mix active samples into the output buffer."""
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

    def _play_sample(self, sample_name: str, volume_multiplier: float = 1.0) -> None:
        """Enqueue a sample for playback with optional resampling."""
        if not self._enabled or not self._audio_available or self._stream is None:
            return

        if sample_name not in self._samples:
            logger.warning("Sample not found: %s", sample_name)
            return

        data, sr = self._samples[sample_name]
        if sr != self._sample_rate:
            try:
                import librosa

                data = librosa.resample(data, sr, self._sample_rate)
            except Exception as exc:
                logger.warning("Resampling failed for %s: %s", sample_name, exc)
                return

        data = np.asarray(data, dtype=self._dtype)
        with self._audio_lock:
            self._active_samples.append(
                QueuedSample(data=data, pos=0, volume=volume_multiplier)
            )

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

    def play_strum(self, direction: str, accent: float = 0.0):
        """Play strum sound based on direction and accent level."""
        if not self._strum_enabled or direction == "-":
            return  # No sound if disabled or for rests

        # Determine sample name - map single letters to full words
        direction_map = {"D": "down", "U": "up"}
        direction_word = direction_map.get(direction, direction.lower())

        if accent > 0.5:
            sample_name = f"strum_{direction_word}_accent"
        else:
            sample_name = f"strum_{direction_word}"

        # Calculate volume based on accent
        base_volume = self._strum_volume
        accent_boost = accent * 0.3  # Up to 30% volume boost for accents
        volume = base_volume * (1.0 + accent_boost)

        self._play_sample(sample_name, volume)

    def set_volumes(
        self, click: float = None, strum: float = None, master: float = None
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

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get current audio device information."""
        return self._device_info

    def stop_all(self) -> None:
        """Stop all currently playing sounds."""
        if not self._audio_available or self._stream is None:
            return
        with self._audio_lock:
            self._active_samples.clear()
        self._stream.stop()
        self._stream.start()

    def close(self) -> None:
        """Clean shutdown of audio system."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None


@dataclass
class QueuedSample:
    data: np.ndarray
    pos: int
    volume: float
