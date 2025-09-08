"""Chord progression controls widget."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Song name display (left of button)
        self.song_name_label = QLabel("Песня не выбрана")
        self.song_name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.song_name_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.song_name_label.setWordWrap(True)

        # Next progression button
        self.next_button = QPushButton("Следующая прогрессия ▶")
        self.next_button.clicked.connect(self.next_progression_clicked.emit)
        self.next_button.setEnabled(False)

        layout.addWidget(self.song_name_label)
        layout.addWidget(self.next_button)
        layout.addStretch(1)

    def set_song(self, song):
        """Set the current song and update display."""
        self.current_song = song
        if song:
            self.song_name_label.setText(f"{song.title}\n{song.artist}")
            # Enable button only if there are multiple progressions/sections
            self.next_button.setEnabled(song.has_extended_structure())
        else:
            self.song_name_label.setText("Песня не выбрана")
            self.next_button.setEnabled(False)

    def set_button_enabled(self, enabled: bool):
        """Enable or disable the next progression button."""
        self.next_button.setEnabled(enabled)
