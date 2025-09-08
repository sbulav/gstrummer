"""
Practice coach widget that provides contextual hints and guidance for guitar learning.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from typing import Dict, List, Optional

from app.core.chord_library import get_chord_diagram, BASIC_CHORDS


class PracticeCoach(QWidget):
    """Widget that provides intelligent coaching tips during practice sessions."""
    
    hint_requested = Signal(str)  # Signal when user wants more details
    
    def __init__(self):
        super().__init__()
        self.current_hints = []
        self.hint_history = []
        self.coaching_mode = "beginner"  # beginner, intermediate, advanced
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the coaching UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        coach_icon = QLabel("💡")
        coach_icon.setFont(QFont("Arial", 16))
        header_layout.addWidget(coach_icon)
        
        title = QLabel("Тренер")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-left: 5px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Coaching level selector
        self.level_btn = QPushButton(self.coaching_mode.title())
        self.level_btn.setMaximumWidth(100)
        self.level_btn.clicked.connect(self.cycle_coaching_level)
        header_layout.addWidget(self.level_btn)
        
        layout.addLayout(header_layout)
        
        # Hint display area
        self.hint_display = QTextEdit()
        self.hint_display.setMaximumHeight(120)
        self.hint_display.setReadOnly(True)
        self.hint_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
                font-size: 11px;
                color: #495057;
            }
        """)
        layout.addWidget(self.hint_display)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.next_tip_btn = QPushButton("Следующий совет")
        self.next_tip_btn.clicked.connect(self.show_next_tip)
        self.next_tip_btn.setEnabled(False)
        button_layout.addWidget(self.next_tip_btn)
        
        button_layout.addStretch()
        
        self.details_btn = QPushButton("Подробнее")
        self.details_btn.clicked.connect(self.show_details)
        self.details_btn.setEnabled(False)
        button_layout.addWidget(self.details_btn)
        
        layout.addLayout(button_layout)
        
        # Show initial welcome message
        self.show_welcome_message()
        
    def show_welcome_message(self):
        """Show initial welcome and setup message."""
        welcome_msg = """
        <b>Добро пожаловать в режим изучения песен! 🎸</b><br><br>
        Выберите песню из списка выше, и я помогу вам освоить её пошагово.<br>
        Начинайте медленно и постепенно увеличивайте темп.
        """
        self.hint_display.setHtml(welcome_msg)
        
    def cycle_coaching_level(self):
        """Cycle through coaching levels."""
        levels = ["beginner", "intermediate", "advanced"]
        current_index = levels.index(self.coaching_mode)
        self.coaching_mode = levels[(current_index + 1) % len(levels)]
        self.level_btn.setText(self.coaching_mode.title())
        
        # Update hints based on new level
        self.show_level_change_hint()
        
    def show_level_change_hint(self):
        """Show hint about the new coaching level."""
        hints = {
            "beginner": "Режим новичка: максимум деталей и пошаговые инструкции",
            "intermediate": "Средний уровень: фокус на технике и ритме", 
            "advanced": "Продвинутый: минимум подсказок, акцент на музыкальность"
        }
        
        self.show_hint("level_change", hints[self.coaching_mode])
        
    def analyze_song_difficulty(self, song):
        """Analyze song difficulty and provide appropriate coaching."""
        if not song:
            return
            
        # Analyze chord complexity
        complex_chords = []
        beginner_chords = []
        
        chords = getattr(song, 'all_chords', song.progression if hasattr(song, 'progression') else [])
        
        for chord_name in chords:
            chord_diagram = get_chord_diagram(chord_name)
            if chord_diagram:
                if chord_diagram.difficulty == "advanced":
                    complex_chords.append(chord_name)
                elif chord_diagram.difficulty == "beginner":
                    beginner_chords.append(chord_name)
        
        # Generate coaching based on analysis
        if complex_chords and self.coaching_mode == "beginner":
            self.show_chord_difficulty_hint(complex_chords, song)
        elif song.bpm > 120 and self.coaching_mode in ["beginner", "intermediate"]:
            self.show_tempo_hint(song.bpm)
        else:
            self.show_song_overview_hint(song)
            
    def show_chord_difficulty_hint(self, complex_chords: List[str], song):
        """Show hint about complex chords in the song."""
        chord_list = ", ".join(complex_chords)
        hint = f"""
        <b>Внимание: сложные аккорды!</b><br><br>
        В песне "{song.title}" есть сложные аккорды: <b>{chord_list}</b><br><br>
        <b>Совет:</b> Сначала потренируйтесь переходить между этими аккордами медленно,
        без ритма. Только когда пальцы запомнят позиции, добавляйте бой.
        """
        
        self.show_hint("chord_difficulty", hint)
        self.add_chord_practice_tips(complex_chords)
        
    def show_tempo_hint(self, bpm: int):
        """Show hint about song tempo."""
        hint = f"""
        <b>Быстрый темп: {bpm} BPM</b><br><br>
        Это довольно быстрая песня. Рекомендую:<br>
        • Начать с темпа {max(60, bpm // 2)} BPM<br>
        • Постепенно увеличивать на 5-10 BPM<br>
        • Следить за чистотой смен аккордов<br>
        """
        
        self.show_hint("tempo_warning", hint)
        
    def show_song_overview_hint(self, song):
        """Show general overview and tips for the song."""
        difficulty_emoji = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
        difficulty = getattr(song, 'difficulty', 'beginner')
        
        hint = f"""
        <b>Песня: {song.title}</b> {difficulty_emoji.get(difficulty, '⚪')}<br>
        <b>Исполнитель:</b> {song.artist}<br>
        <b>Темп:</b> {song.bpm} BPM<br><br>
        
        <b>Подготовка:</b><br>
        1. Проверьте аппликатуры всех аккордов<br>
        2. Потренируйте переходы между аккордами<br>
        3. Послушайте оригинал для понимания ритма<br>
        """
        
        self.show_hint("song_overview", hint)
        
    def show_chord_transition_hint(self, from_chord: str, to_chord: str):
        """Show specific hint for chord transitions."""
        from_diagram = get_chord_diagram(from_chord)
        to_diagram = get_chord_diagram(to_chord)
        
        if not from_diagram or not to_diagram:
            return
            
        # Analyze finger movements
        common_fingers = []
        moving_fingers = []
        
        for i, (from_fret, to_fret) in enumerate(zip(from_diagram.frets, to_diagram.frets)):
            if from_fret == to_fret and from_fret > 0:
                common_fingers.append(i + 1)  # String numbers 1-6
            elif from_fret != to_fret:
                moving_fingers.append(i + 1)
                
        hint = f"""
        <b>Переход {from_chord} → {to_chord}</b><br><br>
        """
        
        if common_fingers:
            hint += f"✅ Не двигайте пальцы на струнах: {', '.join(map(str, common_fingers))}<br>"
        
        if moving_fingers:
            hint += f"👆 Переставьте пальцы на струнах: {', '.join(map(str, moving_fingers))}<br>"
            
        hint += "<br><b>Совет:</b> Сначала уберите ненужные пальцы, затем поставьте новые."
        
        self.show_hint("chord_transition", hint)
        
    def show_rhythm_coaching(self, pattern_name: str, step_accuracy: List[float]):
        """Provide coaching based on rhythm accuracy."""
        if not step_accuracy:
            return
            
        avg_accuracy = sum(abs(x) for x in step_accuracy) / len(step_accuracy)
        
        if avg_accuracy > 50:  # More than 50ms off on average
            hint = f"""
            <b>Работа над ритмом</b><br><br>
            Средняя погрешность: {avg_accuracy:.1f} мс<br><br>
            <b>Советы:</b><br>
            • Сконцентрируйтесь на метрономе<br>
            • Играйте медленнее, но точнее<br>
            • Считайте вслух: "раз-и-два-и-три-и-четыре-и"<br>
            """
            
            self.show_hint("rhythm_accuracy", hint)
        elif avg_accuracy < 20:  # Very good timing
            self.show_hint("rhythm_good", "🎉 Отличный тайминг! Попробуйте увеличить темп.")
            
    def show_hint(self, hint_type: str, message: str):
        """Show a coaching hint."""
        self.current_hints = [{"type": hint_type, "message": message}]
        self.hint_display.setHtml(message)
        
        self.next_tip_btn.setEnabled(False)
        self.details_btn.setEnabled(True)
        
        # Add to history
        self.hint_history.append({"type": hint_type, "message": message})
        
    def add_chord_practice_tips(self, chords: List[str]):
        """Add specific practice tips for difficult chords."""
        tips = []
        
        for chord in chords:
            chord_diagram = get_chord_diagram(chord)
            if not chord_diagram:
                continue
                
            if chord_diagram.barre:
                tips.append({
                    "type": "barre_tip",
                    "message": f"""
                    <b>Баррэ аккорд {chord}</b><br><br>
                    • Прижимайте указательным пальцем все струны на {chord_diagram.barre} ладу<br>
                    • Большой палец должен быть посередине грифа<br>
                    • Не сжимайте сильно - найдите минимальное усилие<br>
                    • Тренируйте баррэ отдельно без других пальцев
                    """
                })
                
        if tips:
            self.current_hints.extend(tips)
            self.next_tip_btn.setEnabled(True)
            
    def show_next_tip(self):
        """Show the next available tip."""
        if len(self.current_hints) > 1:
            self.current_hints.pop(0)
            current_tip = self.current_hints[0]
            self.hint_display.setHtml(current_tip["message"])
            
            if len(self.current_hints) <= 1:
                self.next_tip_btn.setEnabled(False)
                
    def show_details(self):
        """Show detailed information about the current hint."""
        if not self.current_hints:
            return
            
        current_hint = self.current_hints[0]
        self.hint_requested.emit(current_hint["type"])
        
    def update_for_practice_session(self, song, pattern, current_section=None):
        """Update coaching based on current practice session."""
        if not song:
            self.show_welcome_message()
            return
            
        # Analyze and provide initial coaching
        self.analyze_song_difficulty(song)
        
        # Set up section-specific coaching if available
        if current_section and hasattr(current_section, 'chords'):
            self.prepare_section_coaching(current_section)
            
    def prepare_section_coaching(self, section):
        """Prepare coaching tips specific to a song section."""
        if len(section.chords) >= 2:
            # Prepare transition tips for consecutive chords
            for i in range(len(section.chords) - 1):
                from_chord = section.chords[i]
                to_chord = section.chords[i + 1]
                
                # Add transition tip to queue
                tip = {
                    "type": "section_transition",
                    "message": f"Подготовьте переход {from_chord} → {to_chord} в этой секции"
                }
                
                if not hasattr(self, 'section_tips'):
                    self.section_tips = []
                self.section_tips.append(tip)