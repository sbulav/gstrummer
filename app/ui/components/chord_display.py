"""Chord display widget for showing current chord progression."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


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
        
        # Create chord labels
        for i, chord in enumerate(chords):
            chord_label = QLabel(chord)
            chord_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            chord_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chord_label.setMinimumWidth(80)
            chord_label.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 2px;
                    color: #333;
                }
            """)
            
            self.chord_labels.append(chord_label)
            self.chord_layout.insertWidget(len(self.chord_labels), chord_label)

    def clear_chords(self):
        """Clear all chord labels."""
        for label in self.chord_labels:
            label.hide()
            self.chord_layout.removeWidget(label)
            label.deleteLater()
        self.chord_labels.clear()

    def show_no_chords(self, message: str):
        """Show a message when no chords are available."""
        self.no_chords_label.setText(message)
        self.no_chords_label.show()

    def highlight_chord(self, chord_index: int):
        """Highlight a specific chord in the progression."""
        for i, label in enumerate(self.chord_labels):
            if i == chord_index:
                label.setStyleSheet("""
                    QLabel {
                        background-color: #4CAF50;
                        border: 2px solid #45a049;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 2px;
                        color: white;
                        font-weight: bold;
                    }
                """)
            else:
                label.setStyleSheet("""
                    QLabel {
                        background-color: #f0f0f0;
                        border: 2px solid #ddd;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 2px;
                        color: #333;
                    }
                """)

    def clear_highlight(self):
        """Clear chord highlighting."""
        for label in self.chord_labels:
            label.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 2px;
                    color: #333;
                }
            """)