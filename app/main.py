import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QComboBox, 
                              QSlider, QGroupBox, QStackedWidget, QMessageBox,
                              QSplashScreen)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from core.patterns import load_patterns, load_songs
from core.metronome import Metronome
from core.audio_engine import AudioEngine
from ui.practice_view import PracticeView


class MainWindow(QMainWindow):
    """Enhanced main window with improved UI and integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GStrummer - Гитарные ритмы")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Initialize core components
        self.audio_engine = AudioEngine()
        self.metronome = Metronome()
        
        # Load data with error handling
        self.patterns = {}
        self.songs = []
        self.load_data()
        
        self.current_pattern = None
        self.current_song = None
        
        self.init_ui()
        self.setup_connections()
        
        # Apply stylesheet
        self.apply_stylesheet()
        
    def load_data(self):
        """Load patterns and songs with comprehensive error handling."""
        try:
            self.patterns = load_patterns("app/data/patterns.yaml")
            print(f"Loaded {len(self.patterns)} patterns")
        except Exception as e:
            print(f"Error loading patterns: {e}")
            QMessageBox.warning(self, "Ошибка загрузки", 
                              f"Не удалось загрузить ритмы:\n{e}")
            # Use fallback patterns
            self.patterns = self.create_fallback_patterns()
            
        try:
            self.songs = load_songs("app/data/songs.yaml")
            print(f"Loaded {len(self.songs)} songs")
        except Exception as e:
            print(f"Error loading songs: {e}")
            # Continue without songs
            self.songs = []
        
    def create_fallback_patterns(self):
        """Create basic fallback patterns if YAML loading fails."""
        from core.patterns import StrumPattern, Step
        
        rock_steps = [
            Step(0.0, "D", 0.7),
            Step(0.125, "U"),
            Step(0.25, "D", 1.0),
            Step(0.375, "U"),
            Step(0.5, "D", 0.7),
            Step(0.625, "U"),
            Step(0.75, "D", 1.0),
            Step(0.875, "U")
        ]
        
        rock_pattern = StrumPattern(
            id="rock_8",
            name="Рок-восьмушки (встроенный)",
            time_sig=(4, 4),
            steps_per_bar=8,
            steps=rock_steps,
            bpm_default=92,
            bpm_min=60,
            bpm_max=140,
            notes="Базовый рок-ритм с акцентами на 2 и 4 доли"
        )
        
        return {"rock_8": rock_pattern}
        
    def init_ui(self):
        """Initialize the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content (stacked views)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create views
        self.main_menu = self.create_main_menu()
        self.practice_view = PracticeView(self.audio_engine, self.metronome)
        
        # Add views to stack
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.practice_view)
        
        # Start with main menu
        self.show_main_menu()
        
    def create_header(self):
        """Create application header."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # App title
        title = QLabel("🎸 GStrummer")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Version info
        version_label = QLabel("v1.0")
        version_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        header_layout.addWidget(version_label)
        
        return header_widget
        
    def setup_connections(self):
        """Setup signal connections."""
        # Practice view connections
        self.practice_view.back_requested.connect(self.show_main_menu)
        
        # Metronome connections for status updates
        self.metronome.started.connect(lambda: self.statusBar().showMessage("Метроном запущен"))
        self.metronome.stopped.connect(lambda: self.statusBar().showMessage("Метроном остановлен"))
        
    def create_main_menu(self):
        """Create the main menu interface with improved styling."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Welcome message
        welcome = QLabel("Добро пожаловать в GStrummer!")
        welcome.setFont(QFont("Arial", 16))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("margin: 20px; color: #34495e;")
        layout.addWidget(welcome)
        
        # Main content in horizontal layout
        content_layout = QHBoxLayout()
        
        # Left side - Modes and patterns
        left_layout = QVBoxLayout()
        
        # Modes
        mode_group = QGroupBox("🎯 Режимы обучения")
        mode_layout = QVBoxLayout()
        mode_group.setLayout(mode_layout)
        
        practice_btn = QPushButton("🎵 Практика ритмов")
        practice_btn.setMinimumHeight(50)
        practice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        practice_btn.clicked.connect(self.show_practice)
        mode_layout.addWidget(practice_btn)
        
        quiz_btn = QPushButton("🎲 Викторина (скоро)")
        quiz_btn.setMinimumHeight(40)
        quiz_btn.setEnabled(False)
        quiz_btn.setStyleSheet("background-color: #bdc3c7; color: #7f8c8d; border-radius: 6px;")
        mode_layout.addWidget(quiz_btn)
        
        song_btn = QPushButton("🎤 Песни (скоро)")
        song_btn.setMinimumHeight(40)
        song_btn.setEnabled(False)
        song_btn.setStyleSheet("background-color: #bdc3c7; color: #7f8c8d; border-radius: 6px;")
        mode_layout.addWidget(song_btn)
        
        left_layout.addWidget(mode_group)
        
        # Pattern selection
        pattern_group = QGroupBox("🎸 Доступные ритмы")
        pattern_layout = QVBoxLayout()
        pattern_group.setLayout(pattern_layout)
        
        pattern_layout.addWidget(QLabel("Выберите ритм для практики:"))
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.setMinimumHeight(35)
        for pattern_id, pattern in self.patterns.items():
            self.pattern_combo.addItem(pattern.name, pattern_id)
        self.pattern_combo.currentTextChanged.connect(self.on_pattern_preview)
        pattern_layout.addWidget(self.pattern_combo)
        
        # Pattern preview info
        self.pattern_preview = QLabel("Выберите ритм для предпросмотра")
        self.pattern_preview.setWordWrap(True)
        self.pattern_preview.setStyleSheet("""
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        """)
        pattern_layout.addWidget(self.pattern_preview)
        
        left_layout.addWidget(pattern_group)
        
        content_layout.addLayout(left_layout)
        
        # Right side - Songs and tips
        right_layout = QVBoxLayout()
        
        # Songs section
        if self.songs:
            song_group = QGroupBox("🎵 Русский рок")
            song_layout = QVBoxLayout()
            song_group.setLayout(song_layout)
            
            song_layout.addWidget(QLabel("Популярные песни:"))
            
            self.song_combo = QComboBox()
            self.song_combo.setMinimumHeight(35)
            for song in self.songs:
                self.song_combo.addItem(f"{song.artist} - {song.title}")
            song_layout.addWidget(self.song_combo)
            
            right_layout.addWidget(song_group)
        
        # Tips section
        tips_group = QGroupBox("💡 Советы")
        tips_layout = QVBoxLayout()
        tips_group.setLayout(tips_layout)
        
        tips_text = """
        • Начинайте с медленного темпа
        • Следите за равномерностью движений
        • Акценты - это динамика, не торопитесь
        • Используйте метроном регулярно
        • Практикуйтесь каждый день понемногу
        """
        
        tips_label = QLabel(tips_text)
        tips_label.setStyleSheet("""
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 15px;
            color: #856404;
        """)
        tips_layout.addWidget(tips_label)
        
        right_layout.addWidget(tips_group)
        right_layout.addStretch()
        
        content_layout.addLayout(right_layout)
        layout.addLayout(content_layout)
        
        # Show pattern preview on startup
        if self.patterns:
            self.on_pattern_preview()
        
        return widget
    
    def on_pattern_preview(self):
        """Update pattern preview when selection changes."""
        pattern_id = self.pattern_combo.currentData()
        if pattern_id and pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            
            time_sig = f"{pattern.time_sig[0]}/{pattern.time_sig[1]}"
            preview_text = f"""
<b>{pattern.name}</b><br>
<b>Размер:</b> {time_sig} | <b>Темп:</b> {pattern.bpm_default} BPM ({pattern.bpm_min}-{pattern.bpm_max})<br>
<b>Шагов в такте:</b> {pattern.steps_per_bar}<br><br>
<i>{pattern.notes}</i>
            """.strip()
            
            self.pattern_preview.setText(preview_text)
    
    def show_main_menu(self):
        """Show the main menu and stop any practice."""
        self.stacked_widget.setCurrentIndex(0)
        self.metronome.stop()
        self.practice_view.cleanup()
        self.statusBar().showMessage("Готов к работе")
    
    def show_practice(self):
        """Show practice view with selected pattern."""
        pattern_id = self.pattern_combo.currentData()
        if pattern_id and pattern_id in self.patterns:
            self.current_pattern = self.patterns[pattern_id]
            
            # Setup practice view
            self.practice_view.set_pattern(self.current_pattern)
            self.practice_view.set_patterns(self.patterns)
            
            # Select the same pattern in practice view
            self.practice_view.transport.select_pattern(pattern_id)
            
            self.stacked_widget.setCurrentIndex(1)
            self.statusBar().showMessage(f"Практика: {self.current_pattern.name}")
        else:
            QMessageBox.warning(self, "Выбор ритма", 
                              "Пожалуйста, выберите ритм для практики")
    
    def apply_stylesheet(self):
        """Apply global stylesheet to the application."""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            color: #2c3e50;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 10px;
            background-color: #f8f9fa;
        }
        
        QComboBox {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 5px;
            background-color: white;
        }
        
        QComboBox:focus {
            border: 2px solid #3498db;
        }
        
        QPushButton {
            border: 1px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px 16px;
            background-color: #ecf0f1;
            font-size: 12px;
        }
        
        QPushButton:hover {
            background-color: #d5dbdb;
        }
        
        QPushButton:pressed {
            background-color: #bdc3c7;
        }
        
        QPushButton:disabled {
            color: #95a5a6;
            background-color: #f8f9fa;
        }
        """
        self.setStyleSheet(style)
    
    def closeEvent(self, event):
        """Handle application close event."""
        self.metronome.stop()
        self.audio_engine.close()
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("GStrummer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("GStrummer")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    try:
        return app.exec()
    except SystemExit as e:
        return e.code
    finally:
        # Cleanup
        if 'window' in locals():
            window.metronome.stop()
            window.audio_engine.close()


if __name__ == "__main__":
    sys.exit(main())