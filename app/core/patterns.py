from dataclasses import dataclass
from typing import List, Tuple, Literal, Optional


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


def load_patterns(path: str = "data/patterns.yaml") -> dict[str, StrumPattern]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    
    patterns = []
    for pattern_data in raw:
        steps = []
        for step_data in pattern_data["steps"]:
            step = Step(
                t=step_data["t"],
                dir=step_data["dir"],
                accent=step_data.get("accent", 0.0),
                technique=step_data.get("technique", "open")
            )
            steps.append(step)
        
        pattern = StrumPattern(
            id=pattern_data["id"],
            name=pattern_data["name"],
            time_sig=tuple(pattern_data["time_sig"]),
            steps_per_bar=pattern_data["steps_per_bar"],
            steps=steps,
            bpm_default=pattern_data["bpm_default"],
            bpm_min=pattern_data["bpm_min"],
            bpm_max=pattern_data["bpm_max"],
            notes=pattern_data["notes"]
        )
        patterns.append(pattern)
    
    return {p.id: p for p in patterns}


def load_songs(path: str = "data/songs.yaml") -> List[Song]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    
    songs = []
    for song_data in raw:
        song = Song(
            title=song_data["title"],
            artist=song_data["artist"],
            bpm=song_data["bpm"],
            time_sig=tuple(song_data["time_sig"]),
            pattern_id=song_data["pattern_id"],
            progression=song_data["progression"],
            notes=song_data["notes"]
        )
        songs.append(song)
    
    return songs