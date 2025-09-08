"""Enhanced chord display widget with fretboard diagrams."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor
from typing import Optional, List

from app.core.chord_library import get_chord_diagram, chord_difficulty_color


class ChordWidget(QWidget):
    """Widget displaying a single chord with name and fretboard diagram."""
    
    def __init__(self, chord_name: str):
        super().__init__()
        self.chord_name = chord_name
        self.chord_diagram = get_chord_diagram(chord_name)
        self.is_highlighted = False
        self.setMinimumSize(100, 140)
        self.setMaximumSize(140, 180)
        
    def paintEvent(self, event):
        """Paint the chord widget with name and diagram."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_color = QColor("#4CAF50") if self.is_highlighted else QColor("#f0f0f0")
        border_color = QColor("#45a049") if self.is_highlighted else QColor("#ddd")
        text_color = QColor("white") if self.is_highlighted else QColor("#333")
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(2, 2, self.width()-4, self.height()-4, 8, 8)
        
        # Chord name
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(QPen(text_color))
        name_rect = painter.boundingRect(0, 5, self.width(), 25, Qt.AlignmentFlag.AlignCenter, self.chord_name)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, self.chord_name)
        
        # Difficulty indicator
        if self.chord_diagram:
            difficulty_color = chord_difficulty_color(self.chord_diagram.difficulty)
            painter.setBrush(QBrush(QColor(difficulty_color)))
            painter.setPen(QPen(QColor(difficulty_color)))
            dot_size = 8
            painter.drawEllipse(self.width() - 15, 8, dot_size, dot_size)
            
            # Mini fretboard diagram
            self._draw_mini_fretboard(painter, 10, 35, self.width()-20, self.height()-50)
        else:
            # No diagram available
            painter.setPen(QPen(QColor("#999")))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(10, 35, self.width()-20, self.height()-50, 
                           Qt.AlignmentFlag.AlignCenter, "Аппликатура\nне найдена")
    
    def _draw_mini_fretboard(self, painter: QPainter, x: int, y: int, width: int, height: int):
        """Draw a mini fretboard diagram."""
        if not self.chord_diagram:
            return
            
        num_strings = 6
        num_frets = 4
        
        string_spacing = width / (num_strings - 1)
        fret_spacing = height / (num_frets + 1)
        
        # Draw strings (vertical lines)
        painter.setPen(QPen(QColor("#C0C0C0"), 1))
        for i in range(num_strings):
            string_x = x + i * string_spacing
            painter.drawLine(int(string_x), y, int(string_x), y + height)
        
        # Draw frets (horizontal lines)
        painter.setPen(QPen(QColor("#666"), 1))
        for i in range(num_frets + 1):
            fret_y = y + i * fret_spacing
            line_width = 2 if i == 0 else 1  # Thicker nut
            painter.setPen(QPen(QColor("#666"), line_width))
            painter.drawLine(x, int(fret_y), x + width, int(fret_y))
        
        # Draw finger positions
        for string_idx, fret in enumerate(self.chord_diagram.frets):
            string_x = x + string_idx * string_spacing
            
            if fret == -1:  # Muted string
                painter.setPen(QPen(QColor("#e74c3c"), 2))
                painter.drawLine(int(string_x - 3), y - 8, int(string_x + 3), y - 2)
                painter.drawLine(int(string_x + 3), y - 8, int(string_x - 3), y - 2)
            elif fret == 0:  # Open string
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                painter.setPen(QPen(QColor("#27ae60"), 2))
                painter.drawEllipse(int(string_x - 4), y - 9, 8, 8)
            elif 1 <= fret <= num_frets:  # Fretted note
                fret_y = y + (fret - 0.5) * fret_spacing
                painter.setBrush(QBrush(QColor("#3498db")))
                painter.setPen(QPen(QColor("#3498db")))
                painter.drawEllipse(int(string_x - 4), int(fret_y - 4), 8, 8)
    
    def set_highlighted(self, highlighted: bool):
        """Set highlight state and update display."""
        self.is_highlighted = highlighted
        self.update()


class ChordDisplayWidget(QWidget):
    """Widget for displaying current chord progression with highlighted current chord."""

    def __init__(self):
        super().__init__()
        self.current_song = None
        self.current_section = None
        self.chord_labels = []
        self.init_ui()

    def init_ui(self):
        """Initialize the chord display UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        self.chord_layout = layout
        
        # Center the chords in the widget
        layout.addStretch()
        
        # Placeholder label
        self.no_chords_label = QLabel("Аккорды не загружены")
        self.no_chords_label.setFont(QFont("Arial", 14))
        self.no_chords_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_chords_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.no_chords_label)
        
        layout.addStretch()

    def set_song(self, song):
        """Set the current song and update chord display."""
        self.current_song = song
        self.update_chord_display()

    def set_section(self, section):
        """Set the current section and update chord display."""
        self.current_section = section
        self.update_chord_display()

    def update_chord_display(self):
        """Update the chord display based on current song and section."""
        # Clear existing chord labels
        self.clear_chords()
        
        if not self.current_song:
            self.show_no_chords("Песня не выбрана")
            return
        
        # Get chords from current section or song
        chords = []
        if self.current_section and hasattr(self.current_section, 'progression'):
            chords = self.current_section.progression
        elif hasattr(self.current_song, 'progression') and self.current_song.progression:
            chords = self.current_song.progression
        elif hasattr(self.current_song, 'all_chords') and self.current_song.all_chords:
            chords = self.current_song.all_chords[:4]  # Show first 4 chords
        
        if not chords:
            self.show_no_chords("Аккорды не указаны")
            return
        
        # Hide no chords label
        self.no_chords_label.hide()
        
        # Create chord widgets with diagrams
        for i, chord in enumerate(chords):
            chord_widget = ChordWidget(chord)
            self.chord_labels.append(chord_widget)
            self.chord_layout.insertWidget(len(self.chord_labels), chord_widget)

    def clear_chords(self):
        """Clear all chord widgets."""
        for widget in self.chord_labels:
            widget.hide()
            self.chord_layout.removeWidget(widget)
            widget.deleteLater()
        self.chord_labels.clear()

    def show_no_chords(self, message: str):
        """Show a message when no chords are available."""
        self.no_chords_label.setText(message)
        self.no_chords_label.show()

    def highlight_chord(self, chord_index: int):
        """Highlight a specific chord in the progression."""
        for i, widget in enumerate(self.chord_labels):
            widget.set_highlighted(i == chord_index)

    def clear_highlight(self):
        """Clear chord highlighting."""
        for widget in self.chord_labels:
            widget.set_highlighted(False)