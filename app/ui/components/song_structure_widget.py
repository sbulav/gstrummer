"""
Song structure visualization widget that shows the overall song layout.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from typing import Optional, List, Dict


class SongStructureWidget(QWidget):
    """Widget that displays the song structure with current position."""
    
    def __init__(self):
        super().__init__()
        self.song = None
        self.current_section = None
        self.current_section_index = 0
        self.setMinimumHeight(80)
        
    def set_song(self, song):
        """Set the song to visualize."""
        self.song = song
        self.current_section = None
        self.current_section_index = 0
        self.update()
        
    def set_current_section(self, section_name: str, section_index: int = 0):
        """Set the currently playing section."""
        self.current_section = section_name
        self.current_section_index = section_index
        self.update()
        
    def paintEvent(self, event):
        """Paint the song structure visualization."""
        if not self.song:
            self._paint_empty_state()
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.song.has_extended_structure():
            self._paint_simple_structure(painter)
        else:
            self._paint_extended_structure(painter)
            
    def _paint_empty_state(self):
        """Paint empty state when no song is loaded."""
        painter = QPainter(self)
        painter.setFont(QFont("Arial", 12))
        painter.setPen(QPen(QColor("#bdc3c7")))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Структура песни")
        
    def _paint_simple_structure(self, painter: QPainter):
        """Paint simple structure for songs without sections."""
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#2c3e50")))
        
        # Simple progression display
        text = f"Прогрессия: {' - '.join(self.song.progression)}"
        painter.drawText(10, 25, text)
        
        # Additional info
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(QColor("#7f8c8d")))
        info_text = f"Паттерн: {self.song.pattern_id} | BPM: {self.song.bpm}"
        painter.drawText(10, 45, info_text)
        
    def _paint_extended_structure(self, painter: QPainter):
        """Paint extended structure with sections."""
        if not self.song.structure:
            return
            
        sections = self.song.get_section_names()
        if not sections:
            return
            
        # Calculate layout
        margin = 10
        section_spacing = 10
        total_width = self.width() - 2 * margin
        section_width = max(60, (total_width - (len(sections) - 1) * section_spacing) // len(sections))
        section_height = 30
        y_pos = (self.height() - section_height) // 2
        
        # Draw sections
        for i, section_name in enumerate(sections):
            x_pos = margin + i * (section_width + section_spacing)
            section = self.song.get_section(section_name)
            
            # Colors based on section type and state
            bg_color, border_color, text_color = self._get_section_colors(
                section_name, i == self.current_section_index
            )
            
            # Draw section box
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawRoundedRect(x_pos, y_pos, section_width, section_height, 6, 6)
            
            # Draw section name
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.setPen(QPen(text_color))
            
            display_name = section_name.replace("_", " ").title()
            painter.drawText(x_pos, y_pos, section_width, section_height,
                           Qt.AlignmentFlag.AlignCenter, display_name)
            
            # Draw repeat indicator if section repeats
            if section and section.repeat > 1:
                painter.setFont(QFont("Arial", 7))
                repeat_text = f"x{section.repeat}"
                painter.drawText(x_pos + section_width - 15, y_pos - 5, repeat_text)
                
        # Draw progress indicator
        if self.current_section_index < len(sections):
            self._draw_progress_arrow(painter, margin, section_width, 
                                    section_spacing, y_pos, section_height)
                                    
    def _get_section_colors(self, section_name: str, is_current: bool):
        """Get colors for a section based on its type and state."""
        # Section type colors
        section_colors = {
            "intro": ("#e8f5e8", "#4caf50", "#2e7d32"),     # Green
            "verse": ("#e3f2fd", "#2196f3", "#1565c0"),     # Blue  
            "pre_chorus": ("#fff3e0", "#ff9800", "#e65100"), # Orange
            "chorus": ("#fce4ec", "#e91e63", "#ad1457"),     # Pink
            "bridge": ("#f3e5f5", "#9c27b0", "#6a1b9a"),    # Purple
            "outro": ("#efebe9", "#795548", "#4e342e"),      # Brown
        }
        
        # Default colors
        default_colors = ("#f5f5f5", "#9e9e9e", "#424242")  # Gray
        bg_color, border_color, text_color = section_colors.get(section_name, default_colors)
        
        if is_current:
            # Highlight current section
            bg_color = "#ffeb3b"  # Yellow highlight
            border_color = "#fbc02d"
            text_color = "#f57f17"
            
        return QColor(bg_color), QColor(border_color), QColor(text_color)
        
    def _draw_progress_arrow(self, painter: QPainter, margin: int, section_width: int,
                           section_spacing: int, y_pos: int, section_height: int):
        """Draw an arrow pointing to the current section."""
        arrow_x = margin + self.current_section_index * (section_width + section_spacing) + section_width // 2
        arrow_y = y_pos + section_height + 10
        
        # Draw arrow pointing up to current section
        painter.setBrush(QBrush(QColor("#f44336")))  # Red arrow
        painter.setPen(QPen(QColor("#f44336")))
        
        # Arrow points
        points = [
            (arrow_x, arrow_y - 10),      # Top point
            (arrow_x - 8, arrow_y),       # Bottom left
            (arrow_x - 3, arrow_y),       # Bottom left inner
            (arrow_x - 3, arrow_y + 5),   # Bottom left stem
            (arrow_x + 3, arrow_y + 5),   # Bottom right stem
            (arrow_x + 3, arrow_y),       # Bottom right inner
            (arrow_x + 8, arrow_y),       # Bottom right
        ]
        
        from PySide6.QtGui import QPolygon
        from PySide6.QtCore import QPoint
        
        polygon = QPolygon([QPoint(x, y) for x, y in points])
        painter.drawPolygon(polygon)
        
    def get_section_info(self) -> Optional[Dict]:
        """Get information about the current section."""
        if not self.song or not self.current_section:
            return None
            
        section = self.song.get_section(self.current_section)
        if not section:
            return None
            
        return {
            "name": self.current_section,
            "display_name": self.current_section.replace("_", " ").title(),
            "chords": section.chords,
            "pattern": section.pattern,
            "bars": section.bars,
            "repeat": section.repeat,
            "bpm_override": section.bpm_override
        }