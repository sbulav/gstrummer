#!/usr/bin/env python3
"""Console interface for practicing guitar strum patterns and songs."""

import os
import time
import threading
from typing import Callable, Dict, Optional

from app.core.patterns import StrumPattern, Song, load_patterns, load_songs


class Metronome:
    def __init__(self, bpm: int = 120, steps_per_beat: int = 2):
        self.bpm = bpm
        self.steps_per_beat = steps_per_beat
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Callable[[float, int], None] = lambda ts, idx: None
        self._current_step = 0

    def set_bpm(self, bpm: int) -> None:
        self.bpm = max(30, min(300, bpm))

    def set_callback(self, callback: Callable[[float, int], None]) -> None:
        self._callback = callback

    def _run(self) -> None:
        step_duration = 60.0 / self.bpm / self.steps_per_beat
        next_time = time.perf_counter()
        while self._running:
            current_time = time.perf_counter()
            if current_time >= next_time:
                self._callback(current_time, self._current_step)
                self._current_step += 1
                next_time += step_duration
            time.sleep(max(0, next_time - time.perf_counter() - 0.001))

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._current_step = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def is_running(self) -> bool:
        return self._running


class AudioEngine:
    def __init__(self) -> None:
        self._enabled = True
        self._click_enabled = True
        self._strum_enabled = True

    def play_click(self, accent: bool = False) -> None:
        if not self._enabled or not self._click_enabled:
            return
        print("CLICK" + ("!" if accent else ""))

    def play_strum(self, direction: str, accent: float = 0.0) -> None:
        if not self._enabled or not self._strum_enabled or direction == "-":
            return
        accent_str = " (ACCENT)" if accent > 0.5 else ""
        print(f"STRUM {direction}{accent_str}")

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def set_click_enabled(self, enabled: bool) -> None:
        self._click_enabled = enabled

    def set_strum_enabled(self, enabled: bool) -> None:
        self._strum_enabled = enabled

    def is_click_enabled(self) -> bool:
        return self._click_enabled

    def is_strum_enabled(self) -> bool:
        return self._strum_enabled

    def close(self) -> None:
        pass


class PatternVisualizer:
    def __init__(self, width: int = 60) -> None:
        self.width = width

    def draw_timeline(
        self,
        pattern: StrumPattern,
        current_step: int,
        bpm: int,
        chord: Optional[str] = None,
    ) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        bar_length = pattern.steps_per_bar
        current_bar_step = current_step % bar_length

        print("=" * self.width)
        line = f"Бой: {pattern.name} | BPM: {bpm}"
        if chord:
            line += f" | Аккорд: {chord}"
        print(line)
        print("-" * self.width)

        timeline: list[str] = []
        beat_labels: list[str] = []
        for i in range(bar_length):
            step = pattern.steps[i]
            if i % (bar_length // pattern.time_sig[0]) == 0:
                beat_labels.append(str(i // (bar_length // pattern.time_sig[0]) + 1))
            else:
                beat_labels.append(" ")
            if i == current_bar_step:
                if step.dir == "D":
                    timeline.append("[↓]")
                elif step.dir == "U":
                    timeline.append("[↑]")
                else:
                    timeline.append("[ ]")
            else:
                if step.dir == "D":
                    timeline.append(" ↓ ")
                elif step.dir == "U":
                    timeline.append(" ↑ ")
                else:
                    timeline.append("   ")

        print("Биты:   " + " ".join(beat_labels))
        print("Ритм:   " + " ".join(timeline))

        accents: list[str] = []
        for step in pattern.steps:
            if step.accent > 0.7:
                accents.append("●")
            elif step.accent > 0.3:
                accents.append("○")
            else:
                accents.append(" ")
        print("Акценты: " + " ".join(accents))

        print("-" * self.width)
        print(f"Шаг: {current_bar_step + 1}/{bar_length}")
        print("=" * self.width)


class GuitarTrainer:
    def __init__(self) -> None:
        self.audio = AudioEngine()
        self.metronome = Metronome()
        self.visualizer = PatternVisualizer()

        self.patterns: Dict[str, StrumPattern] = load_patterns("app/data/patterns.yaml")
        self.songs = load_songs("app/data/songs.yaml")
        self.current_pattern: Optional[StrumPattern] = None
        self.current_song: Optional[Song] = None
        self.running = False

    def on_tick(self, timestamp: float, step_index: int) -> None:
        if not self.current_pattern:
            return
        bar_length = self.current_pattern.steps_per_bar
        bar_step = step_index % bar_length

        if bar_step < len(self.current_pattern.steps):
            step = self.current_pattern.steps[bar_step]
            if step.dir != "-":
                self.audio.play_strum(step.dir, step.accent)
            if bar_step == 0:
                self.audio.play_click(accent=True)
            elif bar_step % (bar_length // self.current_pattern.time_sig[0]) == 0:
                self.audio.play_click()

        chord: Optional[str] = None
        if self.current_song:
            bar_index = step_index // bar_length
            chord = self.current_song.progression[
                bar_index % len(self.current_song.progression)
            ]
        self.visualizer.draw_timeline(
            self.current_pattern, step_index, self.metronome.bpm, chord
        )

    def start_practice(self, pattern_id: str, bpm: Optional[int] = None) -> None:
        if pattern_id not in self.patterns:
            print(f"Паттерн {pattern_id} не найден!")
            return

        self.current_pattern = self.patterns[pattern_id]
        if bpm is not None:
            self.metronome.set_bpm(bpm)
        else:
            self.metronome.set_bpm(self.current_pattern.bpm_default)

        self.metronome.set_callback(self.on_tick)
        self.metronome.steps_per_beat = (
            self.current_pattern.steps_per_bar // self.current_pattern.time_sig[0]
        )

        print(f"Начинаем практику: {self.current_pattern.name}")
        if self.current_song:
            print(f"Песня: {self.current_song.artist} - {self.current_song.title}")
            print(f"Аккорды: {' - '.join(self.current_song.progression)}")
            print(f"Примечания: {self.current_song.notes}")
        print(f"BPM: {self.metronome.bpm}")
        print(
            f"Размер: {self.current_pattern.time_sig[0]}/{self.current_pattern.time_sig[1]}"
        )
        print(f"Описание: {self.current_pattern.notes}")
        print("\n" + "=" * 60)
        print("Управление:")
        print("  [Enter] - пауза/продолжить")
        print("  [+]     - увеличить BPM на 5")
        print("  [-]     - уменьшить BPM на 5")
        print("  [q]     - выход")
        print("=" * 60 + "\n")

        self.running = True
        self.metronome.start()
        try:
            while self.running:
                cmd = input().strip().lower()
                if cmd == "":
                    if self.metronome.is_running():
                        self.metronome.stop()
                        print("Пауза")
                    else:
                        self.metronome.start()
                        print("Продолжаем")
                elif cmd == "+":
                    new_bpm = min(self.current_pattern.bpm_max, self.metronome.bpm + 5)
                    self.metronome.set_bpm(new_bpm)
                    print(f"BPM: {new_bpm}")
                elif cmd == "-":
                    new_bpm = max(self.current_pattern.bpm_min, self.metronome.bpm - 5)
                    self.metronome.set_bpm(new_bpm)
                    print(f"BPM: {new_bpm}")
                elif cmd == "q":
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.metronome.stop()
            self.running = False
            print("\nПрактика завершена!")
            self.current_pattern = None

    def start_song(self, song: Song) -> None:
        self.current_song = song
        try:
            self.start_practice(song.pattern_id, bpm=song.bpm)
        finally:
            self.current_song = None

    def show_menu(self) -> None:
        while True:
            print("\n" + "=" * 60)
            print("           ГИТАРНЫЙ БОЙ - ОБУЧАЮЩАЯ ПРОГРАММА")
            print("=" * 60)
            print("\nДоступные бои:")
            pattern_ids = list(self.patterns.keys())
            for i, pid in enumerate(pattern_ids, 1):
                pattern = self.patterns[pid]
                print(f"{i}. {pattern.name} ({pattern.bpm_default} BPM)")

            print("\nПесни:")
            for i, song in enumerate(self.songs, 1):
                pattern = self.patterns[song.pattern_id]
                print(
                    f"s{i}. {song.artist} - {song.title} "
                    f"({song.bpm} BPM, {pattern.name})"
                )

            print("\nКоманды:")
            print("  1-{}   - выбрать бой".format(len(pattern_ids)))
            print("  sN     - выбрать песню (например, s1)")
            print("  q      - выход")

            choice = input("\nВыберите вариант: ").strip().lower()
            if choice == "q":
                break
            elif choice.startswith("s") and choice[1:].isdigit():
                index = int(choice[1:]) - 1
                if 0 <= index < len(self.songs):
                    self.start_song(self.songs[index])
            elif choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(pattern_ids):
                    self.start_practice(pattern_ids[index])


def main() -> None:
    trainer = GuitarTrainer()
    trainer.show_menu()


if __name__ == "__main__":
    main()
