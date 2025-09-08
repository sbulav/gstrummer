"""
Guitar chord library with fretboard diagrams and fingerings.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ChordDiagram:
    """Represents a guitar chord diagram with fret positions and fingering."""
    name: str
    frets: List[int]  # 6 strings (E-A-D-G-B-E), -1 = muted, 0 = open
    fingers: List[int]  # finger numbers (0 = not played, 1-4 = fingers)
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    barre: Optional[int] = None  # fret number for barre, if any
    description: str = ""


# Basic chord library for beginners
BASIC_CHORDS: Dict[str, ChordDiagram] = {
    # Open chords - easiest for beginners
    "Am": ChordDiagram(
        "Am", [0, 0, 2, 2, 1, 0], [0, 0, 2, 3, 1, 0], 
        "beginner", None, "Ля минор - самый простой аккорд"
    ),
    "C": ChordDiagram(
        "C", [0, 1, 0, 2, 3, -1], [0, 1, 0, 2, 3, 0], 
        "beginner", None, "До мажор - основной аккорд"
    ),
    "D": ChordDiagram(
        "D", [-1, -1, 0, 2, 3, 2], [0, 0, 0, 1, 3, 2], 
        "beginner", None, "Ре мажор"
    ),
    "Dm": ChordDiagram(
        "Dm", [-1, -1, 0, 2, 3, 1], [0, 0, 0, 2, 3, 1], 
        "beginner", None, "Ре минор"
    ),
    "E": ChordDiagram(
        "E", [0, 2, 2, 1, 0, 0], [0, 2, 3, 1, 0, 0], 
        "beginner", None, "Ми мажор"
    ),
    "Em": ChordDiagram(
        "Em", [0, 2, 2, 0, 0, 0], [0, 2, 3, 0, 0, 0], 
        "beginner", None, "Ми минор - очень простой"
    ),
    "G": ChordDiagram(
        "G", [3, 2, 0, 0, 3, 3], [3, 1, 0, 0, 4, 4], 
        "beginner", None, "Соль мажор"
    ),
    "A": ChordDiagram(
        "A", [0, 0, 2, 2, 2, 0], [0, 0, 1, 2, 3, 0], 
        "beginner", None, "Ля мажор"
    ),
    
    # Intermediate chords with barre
    "F": ChordDiagram(
        "F", [1, 1, 3, 3, 2, 1], [1, 1, 4, 4, 3, 2], 
        "intermediate", 1, "Фа мажор - требует баррэ"
    ),
    "Bm": ChordDiagram(
        "Bm", [2, 2, 4, 4, 3, 2], [1, 1, 3, 4, 2, 1], 
        "intermediate", 2, "Си минор - баррэ на 2 ладу"
    ),
    
    # Extended chords for advanced songs
    "Em7": ChordDiagram(
        "Em7", [0, 2, 2, 0, 3, 0], [0, 2, 3, 0, 4, 0], 
        "intermediate", None, "Ми минор септаккорд"
    ),
    "Am7": ChordDiagram(
        "Am7", [0, 0, 2, 0, 1, 0], [0, 0, 2, 0, 1, 0], 
        "beginner", None, "Ля минор септаккорд"
    ),
    "G7": ChordDiagram(
        "G7", [3, 2, 0, 0, 0, 1], [3, 2, 0, 0, 0, 1], 
        "beginner", None, "Соль доминант септаккорд"
    ),
    "Fmaj7": ChordDiagram(
        "Fmaj7", [1, 1, 3, 2, 1, 0], [1, 1, 4, 3, 2, 0], 
        "intermediate", 1, "Фа мажор септаккорд"
    ),
    "Gm7": ChordDiagram(
        "Gm7", [3, 5, 3, 3, 3, 3], [1, 3, 1, 1, 1, 1], 
        "intermediate", 3, "Соль минор септаккорд"
    ),
    "F#7": ChordDiagram(
        "F#7", [2, 4, 2, 3, 2, 2], [1, 3, 1, 4, 1, 1], 
        "advanced", 2, "Фа диез доминант септаккорд"
    ),
    "Bbmaj7": ChordDiagram(
        "Bbmaj7", [1, 1, 3, 2, 3, 1], [1, 1, 3, 2, 4, 1], 
        "advanced", 1, "Си-бемоль мажор септаккорд"
    ),
    "Eb7": ChordDiagram(
        "Eb7", [6, 6, 8, 6, 8, 6], [1, 1, 3, 1, 4, 1], 
        "advanced", 6, "Ми-бемоль доминант септаккорд"
    ),
}


def get_chord_diagram(chord_name: str) -> Optional[ChordDiagram]:
    """Get chord diagram by name."""
    return BASIC_CHORDS.get(chord_name)


def get_chords_by_difficulty(difficulty: str) -> List[ChordDiagram]:
    """Get all chords of specified difficulty level."""
    return [chord for chord in BASIC_CHORDS.values() if chord.difficulty == difficulty]


def get_chord_suggestions(chord_list: List[str]) -> List[str]:
    """Get beginner-friendly alternatives for complex chords."""
    suggestions = []
    for chord in chord_list:
        if chord in BASIC_CHORDS:
            diagram = BASIC_CHORDS[chord]
            if diagram.difficulty == "advanced":
                # Suggest simpler alternatives
                if chord.endswith("maj7"):
                    base = chord.replace("maj7", "")
                    suggestions.append(f"Попробуйте {base} вместо {chord}")
                elif chord.endswith("7"):
                    base = chord.replace("7", "")
                    suggestions.append(f"Попробуйте {base} вместо {chord}")
        else:
            suggestions.append(f"Аккорд {chord} не найден в библиотеке")
    return suggestions


def chord_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level."""
    colors = {
        "beginner": "#2ecc71",    # green
        "intermediate": "#f39c12", # orange
        "advanced": "#e74c3c"      # red
    }
    return colors.get(difficulty, "#95a5a6")  # gray default