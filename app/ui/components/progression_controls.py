"""Chord progression controls widget."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ProgressionControlsWidget(QWidget):
    """Widget for progression controls with next progression button and song name."""

    next_progression_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.current_song = None
        self.init_ui()

    def init_ui(self):
        """Initialize the progression controls UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Song name display (centered)
        self.song_name_label = QLabel("Песня не выбрана")
        self.song_name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.song_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Next progression button (below label)
        self.next_button = QPushButton("Следующая прогрессия ▶")
        self.next_button.clicked.connect(self.next_progression_clicked.emit)
        self.next_button.setEnabled(False)

        layout.addStretch(1)
        layout.addWidget(self.song_name_label)
        layout.addWidget(self.next_button)
        layout.addStretch(1)

    def set_song(self, song):
        """Set the current song and update display."""
        self.current_song = song
        if song:
            self.song_name_label.setText(f"{song.artist} - {song.title}")
            # Enable button only if there are multiple progressions/sections
            self.next_button.setEnabled(song.has_extended_structure())
        else:
            self.song_name_label.setText("Песня не выбрана")
            self.next_button.setEnabled(False)

    def set_button_enabled(self, enabled: bool):
        """Enable or disable the next progression button."""
        self.next_button.setEnabled(enabled)