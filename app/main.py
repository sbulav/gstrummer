import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QComboBox, 
                              QSlider, QGroupBox, QStackedWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core.patterns import load_patterns, load_songs
from core.metronome import Metronome
from core.audio_engine import AudioEngine
from ui.practice_view import PracticeView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Гитарный Бой - Обучающая Программа")
        self.setGeometry(100, 100, 1000, 700)
        
        self.audio_engine = AudioEngine()
        self.metronome = Metronome()
        
        try:
            self.patterns = load_patterns("app/data/patterns.yaml")
            self.songs = load_songs("app/data/songs.yaml")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.patterns = {}
            self.songs = []
        
        self.current_pattern = None
        self.current_song = None
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        title = QLabel("Гитарный Бой")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        self.main_menu = self.create_main_menu()
        self.practice_view = PracticeView(self.audio_engine, self.metronome)
        
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.practice_view)
        
        self.show_main_menu()
    
    def create_main_menu(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        mode_group = QGroupBox("Режимы обучения")
        mode_layout = QVBoxLayout()
        mode_group.setLayout(mode_layout)
        
        practice_btn = QPushButton("Практика боёв")
        practice_btn.clicked.connect(self.show_practice)
        mode_layout.addWidget(practice_btn)
        
        quiz_btn = QPushButton("Викторина (повтори рисунок)")
        quiz_btn.setEnabled(False)
        mode_layout.addWidget(quiz_btn)
        
        song_btn = QPushButton("Играй с песнями")
        song_btn.setEnabled(False)
        mode_layout.addWidget(song_btn)
        
        layout.addWidget(mode_group)
        
        pattern_group = QGroupBox("Доступные бои")
        pattern_layout = QVBoxLayout()
        pattern_group.setLayout(pattern_layout)
        
        self.pattern_combo = QComboBox()
        for pattern_id, pattern in self.patterns.items():
            self.pattern_combo.addItem(pattern.name, pattern_id)
        pattern_layout.addWidget(QLabel("Выберит бой:"))
        pattern_layout.addWidget(self.pattern_combo)
        
        layout.addWidget(pattern_group)
        
        song_group = QGroupBox("Русский рок")
        song_layout = QVBoxLayout()
        song_group.setLayout(song_layout)
        
        self.song_combo = QComboBox()
        for song in self.songs:
            self.song_combo.addItem(f"{song.artist} - {song.title}")
        song_layout.addWidget(QLabel("Популярные песни:"))
        song_layout.addWidget(self.song_combo)
        
        layout.addWidget(song_group)
        
        return widget
    
    def show_main_menu(self):
        self.stacked_widget.setCurrentIndex(0)
        self.metronome.stop()
    
    def show_practice(self):
        pattern_id = self.pattern_combo.currentData()
        if pattern_id in self.patterns:
            self.current_pattern = self.patterns[pattern_id]
            self.practice_view.set_pattern(self.current_pattern)
            self.stacked_widget.setCurrentIndex(1)


def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec())
    except SystemExit:
        window.metronome.stop()
        window.audio_engine.close()


if __name__ == "__main__":
    main()