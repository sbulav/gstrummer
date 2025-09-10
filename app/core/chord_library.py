"""
Guitar chord library with fretboard diagrams and fingerings.
Порядок струн в списках frets/fingers: e–B–G–D–A–E (от 1-й к 6-й),
где -1 = заглушено, 0 = открытая струна.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ChordDiagram:
    """Represents a guitar chord diagram with fret positions and fingering."""

    name: str
    frets: List[int]  # e–B–G–D–A–E (1→6)
    fingers: List[int]  # 0 = не прижимаем; 1–4 = пальцы
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    barre: Optional[int] = None  # номер лада для баррэ (если есть)
    description: str = ""


# --- Aliases (германская нотация) -------------------------------------------

ALIASES: Dict[str, str] = {
    "Hm": "Bm",
    "H": "B",
    "H7": "B7",
    "Hm7": "Bm7",
}


# Basic chord library for beginners
BASIC_CHORDS: Dict[str, ChordDiagram] = {
    # Open chords - easiest for beginners
    "Am": ChordDiagram(
        "Am",
        [0, 1, 2, 2, 0, 0],
        [0, 1, 2, 3, 0, 0],
        "beginner",
        None,
        "Ля минор - самый простой аккорд",
    ),
    "C": ChordDiagram(
        "C",
        [0, 1, 0, 2, 3, -1],
        [0, 1, 0, 2, 3, 0],
        "beginner",
        None,
        "До мажор - основной аккорд",
    ),
    "D": ChordDiagram(
        "D", [2, 3, 2, 0, -1, -1], [1, 3, 2, 0, 0, 0], "beginner", None, "Ре мажор"
    ),
    "Dm": ChordDiagram(
        "Dm", [1, 3, 2, 0, -1, -1], [1, 3, 2, 0, 0, 0], "beginner", None, "Ре минор"
    ),
    "E": ChordDiagram(
        "E", [0, 0, 1, 2, 2, 0], [0, 0, 1, 2, 3, 0], "beginner", None, "Ми мажор"
    ),
    "Em": ChordDiagram(
        "Em",
        [0, 0, 0, 2, 2, 0],
        [0, 0, 0, 2, 3, 0],
        "beginner",
        None,
        "Ми минор - очень простой",
    ),
    "G": ChordDiagram(
        "G", [3, 3, 0, 0, 2, 3], [4, 3, 0, 0, 1, 2], "beginner", None, "Соль мажор"
    ),
    "A": ChordDiagram(
        "A", [0, 2, 2, 2, 0, 0], [0, 1, 2, 3, 0, 0], "beginner", None, "Ля мажор"
    ),
    # Intermediate chords with barre
    "F": ChordDiagram(
        "F",
        [1, 1, 2, 3, 3, 1],
        [1, 1, 2, 3, 4, 1],
        "intermediate",
        1,
        "Фа мажор - требует баррэ",
    ),
    "Bm": ChordDiagram(
        "Bm",
        [2, 3, 4, 4, 2, 2],
        [1, 3, 4, 4, 2, 1],
        "intermediate",
        2,
        "Си минор (Hm) - баррэ на 2 ладу; бас F# допустим",
    ),
    # Новые добавленные B/H вариации
    "B": ChordDiagram(
        "B",
        [2, 4, 4, 4, 2, 2],
        [1, 3, 4, 4, 2, 1],
        "intermediate",
        2,
        "Си мажор (H) — баррэ на 2 ладу",
    ),
    "B7": ChordDiagram(
        "B7",
        [2, 0, 2, 1, 2, -1],
        [3, 0, 4, 1, 2, 0],
        "intermediate",
        None,
        "Си7 (H7) — открытая форма, 6-я глушится",
    ),
    "Bm7": ChordDiagram(
        "Bm7",
        [2, 3, 2, 4, 2, 2],
        [1, 3, 2, 4, 1, 1],
        "intermediate",
        2,
        "Си минор 7 (Hm7) — баррэ на 2 ладу",
    ),
    # Extended chords for advanced songs
    "Em7": ChordDiagram(
        "Em7",
        [0, 3, 0, 2, 2, 0],
        [0, 4, 0, 2, 3, 0],
        "intermediate",
        None,
        "Ми минор септаккорд",
    ),
    "Am7": ChordDiagram(
        "Am7",
        [0, 1, 0, 2, 0, 0],
        [0, 1, 0, 2, 0, 0],
        "beginner",
        None,
        "Ля минор септаккорд",
    ),
    "G7": ChordDiagram(
        "G7",
        [1, 0, 0, 0, 2, 3],
        [1, 0, 0, 0, 2, 3],
        "beginner",
        None,
        "Соль доминант септаккорд",
    ),
    "Fmaj7": ChordDiagram(
        "Fmaj7",
        [0, 1, 2, 3, 1, 1],
        [0, 1, 3, 4, 2, 1],
        "intermediate",
        1,
        "Фа мажор септаккорд",
    ),
    "Gm7": ChordDiagram(
        "Gm7",
        [3, 3, 3, 3, 5, 3],
        [1, 1, 1, 1, 3, 1],
        "intermediate",
        3,
        "Соль минор септаккорд",
    ),
    "F#7": ChordDiagram(
        "F#7",
        [2, 2, 3, 2, 4, 2],
        [1, 1, 4, 1, 3, 1],
        "advanced",
        2,
        "Фа диез доминант септаккорд",
    ),
    "Bbmaj7": ChordDiagram(
        "Bbmaj7",
        [1, 3, 2, 3, 1, 1],
        [1, 3, 2, 4, 1, 1],
        "advanced",
        1,
        "Си-бемоль мажор септаккорд",
    ),
    "Eb7": ChordDiagram(
        "Eb7",
        [6, 8, 6, 8, 6, 6],
        [1, 4, 1, 3, 1, 1],
        "advanced",
        6,
        "Ми-бемоль доминант септаккорд",
    ),
}


def _resolve_alias(chord_name: str) -> str:
    """Map aliases (e.g., Hm -> Bm) to canonical names."""
    return ALIASES.get(chord_name, chord_name)


def get_chord_diagram(chord_name: str) -> Optional[ChordDiagram]:
    """Get chord diagram by name (supports aliases like Hm/H/H7/Hm7)."""
    return BASIC_CHORDS.get(_resolve_alias(chord_name))


def get_chords_by_difficulty(difficulty: str) -> List[ChordDiagram]:
    """Get all chords of specified difficulty level."""
    return [chord for chord in BASIC_CHORDS.values() if chord.difficulty == difficulty]


def get_chord_suggestions(chord_list: List[str]) -> List[str]:
    """Get beginner-friendly alternatives for complex chords."""
    suggestions = []
    for chord in chord_list:
        key = _resolve_alias(chord)
        if key in BASIC_CHORDS:
            diagram = BASIC_CHORDS[key]
            if diagram.difficulty == "advanced":
                if key.endswith("maj7"):
                    base = key.replace("maj7", "")
                    suggestions.append(f"Попробуйте {base} вместо {chord}")
                elif key.endswith("7"):
                    base = key.replace("7", "")
                    suggestions.append(f"Попробуйте {base} вместо {chord}")
        else:
            suggestions.append(f"Аккорд {chord} не найден в библиотеке")
    return suggestions


def chord_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level."""
    colors = {
        "beginner": "#2ecc71",  # green
        "intermediate": "#f39c12",  # orange
        "advanced": "#e74c3c",  # red
    }
    return colors.get(difficulty, "#95a5a6")  # gray default
