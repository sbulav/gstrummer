from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Optional, Dict, Any


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
class SongSection:
    """Represents a section of a song (verse, chorus, etc.)"""
    name: str
    chords: List[str]
    pattern: str  # pattern_id to use for this section
    bars: int = 4
    repeat: int = 1
    bpm_override: Optional[int] = None


@dataclass
class Song:
    title: str
    artist: str
    bpm: int
    time_sig: Tuple[int, int]
    pattern_id: str
    progression: List[str]
    notes: str
    # New optional fields for extended song structure
    structure: Optional[Dict[str, SongSection]] = None
    all_chords: Optional[List[str]] = None
    difficulty: Optional[str] = None
    
    def __post_init__(self):
        """Initialize all_chords from progression if not provided"""
        if self.all_chords is None:
            if self.structure:
                # Collect all unique chords from all sections
                chords_set = set()
                for section in self.structure.values():
                    chords_set.update(section.chords)
                self.all_chords = sorted(list(chords_set))
            else:
                # Use progression as all_chords for backward compatibility
                self.all_chords = list(self.progression)
    
    def has_extended_structure(self) -> bool:
        """Check if this song uses the extended structure format"""
        return self.structure is not None
    
    def get_section(self, section_name: str) -> Optional[SongSection]:
        """Get a specific section by name"""
        if not self.structure:
            return None
        return self.structure.get(section_name)
    
    def get_section_names(self) -> List[str]:
        """Get list of all section names in order"""
        if not self.structure:
            return []
        # Common order for sections
        order = ["intro", "verse", "pre_chorus", "chorus", "bridge", "outro"]
        sections = []
        for section_name in order:
            if section_name in self.structure:
                sections.append(section_name)
        # Add any remaining sections not in the standard order
        for section_name in self.structure:
            if section_name not in sections:
                sections.append(section_name)
        return sections


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
        # Parse structure if present
        structure = None
        if "structure" in song_data:
            structure = {}
            for section_name, section_data in song_data["structure"].items():
                structure[section_name] = SongSection(
                    name=section_name,
                    chords=section_data["chords"],
                    pattern=section_data.get("pattern", song_data["pattern_id"]),
                    bars=section_data.get("bars", 4),
                    repeat=section_data.get("repeat", 1),
                    bpm_override=section_data.get("bpm_override")
                )
        
        song = Song(
            title=song_data["title"],
            artist=song_data["artist"],
            bpm=song_data["bpm"],
            time_sig=tuple(song_data["time_sig"]),
            pattern_id=song_data["pattern_id"],
            progression=song_data["progression"],
            notes=song_data["notes"],
            structure=structure,
            all_chords=song_data.get("all_chords"),
            difficulty=song_data.get("difficulty")
        )
        songs.append(song)
    
    return songs
