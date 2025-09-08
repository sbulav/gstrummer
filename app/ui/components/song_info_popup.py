from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SongInfoPopup(QDialog):
    """Popup dialog showing detailed song information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_song = None
        self.setWindowTitle("Информация о песне")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        """Initialize the popup UI."""
        layout = QVBoxLayout(self)

        # Song info text area
        self.song_info = QTextEdit()
        self.song_info.setReadOnly(True)
        layout.addWidget(self.song_info)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Close button
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def set_song(self, song):
        """Set the song to display information for."""
        self.current_song = song
        self.update_song_info()

    def update_song_info(self):
        """Update the song information display."""
        if not self.current_song:
            self.song_info.setText("Песня не выбрана")
            return

        song = self.current_song
        time_sig = f"{song.time_sig[0]}/{song.time_sig[1]}"

        info_text = f"""
<b>Песня:</b> {song.title}<br>
<b>Исполнитель:</b> {song.artist}<br>
<b>Размер:</b> {time_sig}<br>
<b>Темп:</b> {song.bpm} BPM<br>
<b>Сложность:</b> {song.difficulty or "Не указана"}<br><br>
<b>Заметки:</b><br>
{song.notes}
        """.strip()

        if song.has_extended_structure():
            sections = song.get_section_names()
            sections_text = ", ".join([s.replace("_", " ").title() for s in sections])
            info_text += f"<br><br><b>Секции:</b> {sections_text}"

        self.song_info.setHtml(info_text)