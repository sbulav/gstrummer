"""
Fretboard diagram widget for displaying guitar chord fingerings.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QRect
from typing import Optional

from app.core.chord_library import ChordDiagram, get_chord_diagram, chord_difficulty_color


class FretboardDiagramWidget(QWidget):
    """Widget for displaying guitar chord diagrams on a fretboard."""
    
    def __init__(self):
        super().__init__()
        self.chord_diagram: Optional[ChordDiagram] = None
        self.setMinimumSize(120, 160)
        self.setMaximumSize(200, 220)
        
    def set_chord(self, chord_name: str):
        """Set the chord to display."""
        self.chord_diagram = get_chord_diagram(chord_name)
        self.update()
        
    def clear_chord(self):
        """Clear the current chord display."""
        self.chord_diagram = None
        self.update()
        
    def paintEvent(self, event):
        """Paint the fretboard diagram."""
        if not self.chord_diagram:
            self._paint_empty_state()
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate layout
        margin = 20
        chord_area_height = 25
        diagram_width = self.width() - 2 * margin
        diagram_height = self.height() - 2 * margin - chord_area_height
        
        # Draw chord name and difficulty
        self._paint_chord_header(painter, margin, chord_area_height)
        
        # Draw fretboard
        fret_start_y = margin + chord_area_height
        self._paint_fretboard(painter, margin, fret_start_y, diagram_width, diagram_height)
        
    def _paint_empty_state(self):
        """Paint empty state when no chord is selected."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw placeholder text
        painter.setPen(QPen(QColor("#bdc3c7")))
        painter.setFont(QFont("Arial", 10))
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Выберите\nаккорд")
        
    def _paint_chord_header(self, painter: QPainter, margin: int, header_height: int):
        """Paint chord name and difficulty indicator."""
        # Chord name
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#2c3e50")))
        name_rect = QRect(margin, 0, self.width() - 2 * margin, header_height)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, self.chord_diagram.name)
        
        # Difficulty indicator (colored dot)
        difficulty_color = chord_difficulty_color(self.chord_diagram.difficulty)
        painter.setBrush(QBrush(QColor(difficulty_color)))
        painter.setPen(QPen(QColor(difficulty_color)))
        dot_size = 8
        dot_x = self.width() - margin - dot_size
        dot_y = 5
        painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
        
    def _paint_fretboard(self, painter: QPainter, x: int, y: int, width: int, height: int):
        """Paint the fretboard diagram with finger positions."""
        num_frets = 4  # Show 4 frets
        num_strings = 6
        
        string_spacing = width / (num_strings - 1)
        fret_spacing = height / (num_frets + 1)  # +1 for nut
        
        # Colors
        fretboard_color = QColor("#8B4513")  # Brown
        string_color = QColor("#C0C0C0")     # Silver
        fret_color = QColor("#2c3e50")       # Dark
        finger_color = QColor("#3498db")     # Blue
        open_color = QColor("#27ae60")       # Green
        mute_color = QColor("#e74c3c")       # Red
        
        # Draw fretboard background
        painter.setBrush(QBrush(fretboard_color))
        painter.setPen(QPen(fretboard_color))
        painter.drawRect(x, y, width, height)
        
        # Draw strings (vertical lines)
        painter.setPen(QPen(string_color, 2))
        for i in range(num_strings):
            string_x = x + i * string_spacing
            painter.drawLine(int(string_x), y, int(string_x), y + height)
        
        # Draw frets (horizontal lines)
        painter.setPen(QPen(fret_color, 3))
        # Nut (thicker line)
        painter.drawLine(x, y, x + width, y)
        # Regular frets
        painter.setPen(QPen(fret_color, 1))
        for i in range(1, num_frets + 1):
            fret_y = y + i * fret_spacing
            painter.drawLine(x, int(fret_y), x + width, int(fret_y))
            
        # Draw barre if present
        if self.chord_diagram.barre:
            self._paint_barre(painter, x, y, width, string_spacing, fret_spacing, self.chord_diagram.barre)
        
        # Draw finger positions
        for string_idx, (fret, finger) in enumerate(zip(self.chord_diagram.frets, self.chord_diagram.fingers)):
            string_x = x + string_idx * string_spacing
            
            if fret == -1:  # Muted string
                self._paint_mute_symbol(painter, string_x, y - 15, mute_color)
            elif fret == 0:  # Open string
                self._paint_open_symbol(painter, string_x, y - 15, open_color)
            else:  # Fretted note
                fret_y = y + (fret - 0.5) * fret_spacing
                self._paint_finger_position(painter, string_x, fret_y, finger, finger_color)
        
        # Draw string names at bottom
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor("#2c3e50")))
        string_names = ["E", "A", "D", "G", "B", "E"]
        for i, name in enumerate(string_names):
            string_x = x + i * string_spacing
            text_rect = QRect(int(string_x - 10), y + height + 5, 20, 15)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, name)
            
    def _paint_barre(self, painter: QPainter, x: int, y: int, width: int, 
                     string_spacing: float, fret_spacing: float, barre_fret: int):
        """Paint barre line across strings."""
        painter.setPen(QPen(QColor("#3498db"), 4, Qt.PenStyle.SolidLine))
        barre_y = y + (barre_fret - 0.5) * fret_spacing
        painter.drawLine(x, int(barre_y), x + width, int(barre_y))
        
    def _paint_finger_position(self, painter: QPainter, x: float, y: float, 
                              finger: int, color: QColor):
        """Paint a finger position dot."""
        if finger == 0:  # No finger
            return
            
        dot_size = 12
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color))
        painter.drawEllipse(int(x - dot_size/2), int(y - dot_size/2), dot_size, dot_size)
        
        # Draw finger number
        if finger > 0:
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            painter.setPen(QPen(QColor("white")))
            text_rect = QRect(int(x - dot_size/2), int(y - dot_size/2), dot_size, dot_size)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(finger))
            
    def _paint_open_symbol(self, painter: QPainter, x: float, y: float, color: QColor):
        """Paint open string symbol (circle)."""
        symbol_size = 10
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(int(x - symbol_size/2), int(y - symbol_size/2), symbol_size, symbol_size)
        
    def _paint_mute_symbol(self, painter: QPainter, x: float, y: float, color: QColor):
        """Paint muted string symbol (X)."""
        symbol_size = 8
        painter.setPen(QPen(color, 2))
        # Draw X
        painter.drawLine(int(x - symbol_size/2), int(y - symbol_size/2),
                        int(x + symbol_size/2), int(y + symbol_size/2))
        painter.drawLine(int(x + symbol_size/2), int(y - symbol_size/2),
                        int(x - symbol_size/2), int(y + symbol_size/2))


class ChordDisplayWidget(QWidget):
    """Widget that displays multiple chords with fretboard diagrams."""
    
    def __init__(self):
        super().__init__()
        self.chord_progression = []
        self.current_chord_index = 0
        self.setMinimumHeight(160)
        
    def set_progression(self, chords: list):
        """Set the chord progression to display."""
        self.chord_progression = chords
        self.current_chord_index = 0
        self.update()
        
    def set_current_chord(self, index: int):
        """Set the current chord index."""
        if 0 <= index < len(self.chord_progression):
            self.current_chord_index = index
            self.update()
            
    def advance_chord(self):
        """Advance to the next chord in progression."""
        if self.chord_progression:
            self.current_chord_index = (self.current_chord_index + 1) % len(self.chord_progression)
            self.update()
            
    def paintEvent(self, event):
        """Paint the chord progression with diagrams."""
        if not self.chord_progression:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#bdc3c7")))
            painter.setFont(QFont("Arial", 12))
            rect = QRect(0, 0, self.width(), self.height())
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Нет прогрессии")
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate layout for diagrams
        num_chords = len(self.chord_progression)
        diagram_width = min(120, (self.width() - 40) // num_chords)
        diagram_height = self.height() - 20
        total_width = num_chords * diagram_width
        start_x = (self.width() - total_width) // 2
        
        # Draw each chord diagram
        for i, chord_name in enumerate(self.chord_progression):
            x = start_x + i * diagram_width
            
            # Highlight current chord
            if i == self.current_chord_index:
                painter.setBrush(QBrush(QColor(100, 200, 100, 50)))
                painter.setPen(QPen(QColor(100, 200, 100)))
                painter.drawRoundedRect(x - 5, 5, diagram_width, diagram_height - 10, 8, 8)
            
            # Draw chord name
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.setPen(QPen(QColor("#2c3e50")))
            name_rect = QRect(x, 10, diagram_width, 20)
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, chord_name)
            
            # Get chord diagram and draw simplified version
            chord_diagram = get_chord_diagram(chord_name)
            if chord_diagram:
                self._draw_mini_diagram(painter, x + 10, 35, diagram_width - 20, 90, chord_diagram)
                
    def _draw_mini_diagram(self, painter: QPainter, x: int, y: int, width: int, height: int, 
                          chord: ChordDiagram):
        """Draw a simplified mini fretboard diagram."""
        num_strings = 6
        num_frets = 3
        
        string_spacing = width / (num_strings - 1)
        fret_spacing = height / (num_frets + 1)
        
        # Draw strings
        painter.setPen(QPen(QColor("#C0C0C0"), 1))
        for i in range(num_strings):
            string_x = x + i * string_spacing
            painter.drawLine(int(string_x), y, int(string_x), y + height)
            
        # Draw frets
        painter.setPen(QPen(QColor("#2c3e50"), 1))
        for i in range(num_frets + 1):
            fret_y = y + i * fret_spacing
            painter.drawLine(x, int(fret_y), x + width, int(fret_y))
            
        # Draw finger positions (simplified)
        for string_idx, fret in enumerate(chord.frets):
            string_x = x + string_idx * string_spacing
            
            if fret == -1:  # Muted
                painter.setPen(QPen(QColor("#e74c3c"), 1))
                painter.drawLine(int(string_x - 3), y - 8, int(string_x + 3), y - 2)
                painter.drawLine(int(string_x + 3), y - 8, int(string_x - 3), y - 2)
            elif fret == 0:  # Open
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                painter.setPen(QPen(QColor("#27ae60"), 1))
                painter.drawEllipse(int(string_x - 3), y - 8, 6, 6)
            elif 1 <= fret <= num_frets:  # Fretted
                fret_y = y + (fret - 0.5) * fret_spacing
                painter.setBrush(QBrush(QColor("#3498db")))
                painter.setPen(QPen(QColor("#3498db")))
                painter.drawEllipse(int(string_x - 3), int(fret_y - 3), 6, 6)