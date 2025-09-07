#!/usr/bin/env python3
"""
Гитарный Бой - Обучающая программа для гитарных ритмических рисунков
Текстовый интерфейс с визуализацией таймлайна
"""

import time
import threading
from dataclasses import dataclass
from typing import List, Tuple, Literal, Dict, Optional, Callable


@dataclass
class Step:
    t: float
    dir: Literal["D", "U", "-"]
    accent: float = 0.0
    technique: Literal["open", "mute", "palm", "ghost"] = "open"


@dataclass
class StrumPattern:
    id: str
    name: str
    time_sig: Tuple[int, int]
    steps_per_bar: int
    steps: List[Step]
    bpm_default: int
    bpm_min: int
    bpm_max: int
    notes: str


@dataclass
class Song:
    title: str
    artist: str
    bpm: int
    time_sig: Tuple[int, int]
    pattern_id: str
    progression: List[str]
    notes: str


class Metronome:
    def __init__(self, bpm: int = 120, steps_per_beat: int = 2):
        self.bpm = bpm
        self.steps_per_beat = steps_per_beat
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Callable[[float, int], None] = lambda ts, idx: None
        self._current_step = 0

    def set_bpm(self, bpm: int):
        self.bpm = max(30, min(300, bpm))

    def set_callback(self, callback: Callable[[float, int], None]):
        self._callback = callback

    def _run(self):
        step_duration = 60.0 / self.bpm / self.steps_per_beat
        next_time = time.perf_counter()
        
        while self._running:
            current_time = time.perf_counter()
            
            if current_time >= next_time:
                self._callback(current_time, self._current_step)
                self._current_step += 1
                next_time += step_duration
            
            sleep_time = max(0, next_time - time.perf_counter() - 0.001)
            time.sleep(sleep_time)

    def start(self):
        if self._running:
            return
        
        self._running = True
        self._current_step = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def is_running(self) -> bool:
        return self._running


class AudioEngine:
    def __init__(self):
        self._enabled = True
        self._click_enabled = True
        self._strum_enabled = True
        
    def play_click(self, accent: bool = False):
        if not self._enabled or not self._click_enabled:
            return
        print("CLICK" + ("!" if accent else ""))
    
    def play_strum(self, direction: str, accent: float = 0.0):
        if not self._enabled or not self._strum_enabled or direction == "-":
            return
        accent_str = " (ACCENT)" if accent > 0.5 else ""
        print(f"STRUM {direction}{accent_str}")
    
    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        
    def set_click_enabled(self, enabled: bool):
        self._click_enabled = enabled
        
    def set_strum_enabled(self, enabled: bool):
        self._strum_enabled = enabled
        
    def is_click_enabled(self) -> bool:
        return self._click_enabled
        
    def is_strum_enabled(self) -> bool:
        return self._strum_enabled
    
    def close(self):
        pass


class PatternVisualizer:
    def __init__(self, width: int = 60):
        self.width = width
        self.current_pos = 0
        self.metronome = None
        
    def draw_timeline(self, pattern: StrumPattern, current_step: int, current_bpm: int):
        bar_length = pattern.steps_per_bar
        current_bar_step = current_step % bar_length
        
        print("\n" + "=" * self.width)
        print(f"Бой: {pattern.name} | BPM: {current_bpm}")
        print("-" * self.width)
        
        timeline = []
        beat_labels = []
        
        for i in range(bar_length):
            step = pattern.steps[i]
            
            if i % (bar_length // pattern.time_sig[0]) == 0:
                beat_num = (i // (bar_length // pattern.time_sig[0])) + 1
                beat_labels.append(f"{beat_num}")
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
        
        accents = []
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


def create_patterns() -> Dict[str, StrumPattern]:
    patterns = {}
    
    rock_8_steps = [
        Step(0.0, "D", 0.7),
        Step(0.125, "U"),
        Step(0.25, "D", 1.0),
        Step(0.375, "U"),
        Step(0.5, "D", 0.7),
        Step(0.625, "U"),
        Step(0.75, "D", 1.0),
        Step(0.875, "U")
    ]
    
    patterns["rock_8"] = StrumPattern(
        id="rock_8",
        name="Рок-восьмушки (акц. 2 и 4)",
        time_sig=(4, 4),
        steps_per_bar=8,
        steps=rock_8_steps,
        bpm_default=92,
        bpm_min=60,
        bpm_max=140,
        notes="Чередование D/U, акценты на 2 и 4"
    )
    
    ddu_udu_steps = [
        Step(0.0, "D", 0.8),
        Step(0.125, "-"),
        Step(0.25, "D"),
        Step(0.375, "U"),
        Step(0.5, "-"),
        Step(0.625, "U"),
        Step(0.75, "D"),
        Step(0.875, "U")
    ]
    
    patterns["ddu_udu"] = StrumPattern(
        id="ddu_udu",
        name="DDU UDU (баллада)",
        time_sig=(4, 4),
        steps_per_bar=8,
        steps=ddu_udu_steps,
        bpm_default=84,
        bpm_min=56,
        bpm_max=120,
        notes="Популярный балладный рисунок"
    )
    
    return patterns


def create_songs() -> List[Song]:
    return [
        Song(
            title="Группа крови",
            artist="Кино",
            bpm=92,
            time_sig=(4, 4),
            pattern_id="rock_8",
            progression=["Am", "F", "G", "C"],
            notes="Играть плотными восьмушками, акценты 2/4"
        ),
        Song(
            title="Кукушка",
            artist="Кино",
            bpm=78,
            time_sig=(4, 4),
            pattern_id="ddu_udu",
            progression=["Am", "G", "Em", "Am"],
            notes="Балладный вариант; возможны вариации акцентов"
        ),
        Song(
            title="Что такое осень",
            artist="ДДТ",
            bpm=80,
            time_sig=(4, 4),
            pattern_id="ddu_udu",
            progression=["Am", "F", "G", "C"],
            notes="Мягкие апстримы, не торопиться"
        )
    ]


class GuitarTrainer:
    def __init__(self):
        self.audio = AudioEngine()
        self.metronome = Metronome()
        self.visualizer = PatternVisualizer()
        
        self.patterns = create_patterns()
        self.songs = create_songs()
        self.current_pattern = None
        self.running = False
        
    def on_tick(self, timestamp: float, step_index: int):
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
        
        self.visualizer.draw_timeline(self.current_pattern, step_index, self.metronome.bpm)
    
    def start_practice(self, pattern_id: str, bpm: Optional[int] = None):
        if pattern_id not in self.patterns:
            print(f"Паттерн {pattern_id} не найден!")
            return
        
        self.current_pattern = self.patterns[pattern_id]
        
        if bpm:
            self.metronome.set_bpm(bpm)
        else:
            self.metronome.set_bpm(self.current_pattern.bpm_default)
        
        self.metronome.set_callback(self.on_tick)
        self.metronome.steps_per_beat = self.current_pattern.steps_per_bar // self.current_pattern.time_sig[0]
        
        print(f"Начинаем практику: {self.current_pattern.name}")
        print(f"BPM: {self.metronome.bpm}")
        print(f"Размер: {self.current_pattern.time_sig[0]}/{self.current_pattern.time_sig[1]}")
        print(f"Описание: {self.current_pattern.notes}")
        print("\n" + "="*60)
        print("Управление:")
        print("  [Enter] - пауза/продолжить")
        print("  [+]     - увеличить BPM на 5")
        print("  [-]     - уменьшить BPM на 5")
        print("  [q]     - выход")
        print("="*60 + "\n")
        
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
    
    def show_menu(self):
        while True:
            print("\n" + "="*60)
            print("           ГИТАРНЫЙ БОЙ - ОБУЧАЮЩАЯ ПРОГРАММА")
            print("="*60)
            print("\nДоступные бои:")
            
            for i, (pattern_id, pattern) in enumerate(self.patterns.items(), 1):
                print(f"{i}. {pattern.name} ({pattern.bpm_default} BPM)")
            
            print("\nПесни русского рока:")
            for i, song in enumerate(self.songs, 1):
                pattern = self.patterns[song.pattern_id]
                print(f"  {i}. {song.artist} - {song.title} ({song.bpm} BPM, {pattern.name})")
            
            print("\nКоманды:")
            print("  1-{} - выбрать бой для практики".format(len(self.patterns)))
            print("  s    - показать песни")
            print("  q    - выход")
            
            choice = input("\nВыберите вариант: ").strip().lower()
            
            if choice == "q":
                break
            elif choice == "s":
                self.show_songs()
            elif choice.isdigit():
                index = int(choice) - 1
                pattern_ids = list(self.patterns.keys())
                if 0 <= index < len(pattern_ids):
                    pattern_id = pattern_ids[index]
                    self.start_practice(pattern_id)
    
    def show_songs(self):
        print("\n" + "="*60)
        print("ПЕСНИ РУССКОГО РОКА")
        print("="*60)
        
        for i, song in enumerate(self.songs, 1):
            pattern = self.patterns[song.pattern_id]
            print(f"{i}. {song.artist} - {song.title}")
            print(f"   BPM: {song.bpm}, Размер: {song.time_sig[0]}/{song.time_sig[1]}")
            print(f"   Бой: {pattern.name}")
            print(f"   Аккорды: {' - '.join(song.progression)}")
            print(f"   Примечания: {song.notes}")
            print()
        
        input("Нажмите Enter для возврата в меню...")


def main():
    trainer = GuitarTrainer()
    trainer.show_menu()


if __name__ == "__main__":
    main()