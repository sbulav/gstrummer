from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QGroupBox, QTextEdit, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from .components.timeline import TimelineWidget
from .components.transport import TransportControls
from .components.steps_preview import StepsPreviewWidget


class PracticeView(QWidget):
    """Enhanced practice view with visual timeline and transport controls."""
    
    back_requested = Signal()
    
    def __init__(self, audio_engine, metronome):
        super().__init__()
        self.audio = audio_engine
        self.metronome = metronome
        self.current_pattern = None
        self.patterns = {}
        
        self.init_ui()
        self.setup_connections()
        self.setup_shortcuts()
        
    def init_ui(self):
        """Initialize the practice view UI."""
        layout = QVBoxLayout(self)
        
        # Header with back button and pattern info
        header_layout = QHBoxLayout()
        
        self.back_button = QPushButton("← Назад в меню")
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)
        
        header_layout.addStretch()
        
        self.pattern_title = QLabel("Выберите ритм")
        self.pattern_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.pattern_title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.pattern_title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Timeline visualization (main focus) - now with horizontal split
        timeline_group = QGroupBox("Визуализация ритма")
        timeline_layout = QHBoxLayout(timeline_group)
        
        # Horizontal splitter for timeline and preview
        timeline_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Timeline widget (left side)
        self.timeline = TimelineWidget()
        timeline_splitter.addWidget(self.timeline)
        
        # Steps preview (right side)
        self.steps_preview = StepsPreviewWidget()
        timeline_splitter.addWidget(self.steps_preview)
        
        # Set proportions: timeline gets 70%, preview gets 30%
        timeline_splitter.setStretchFactor(0, 7)
        timeline_splitter.setStretchFactor(1, 3)
        
        timeline_layout.addWidget(timeline_splitter)
        
        splitter.addWidget(timeline_group)
        
        # Transport controls and pattern info
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Transport controls
        self.transport = TransportControls()
        controls_layout.addWidget(self.transport)
        
        # Pattern information
        info_group = QGroupBox("Информация о ритме")
        info_layout = QVBoxLayout(info_group)
        
        self.pattern_info = QTextEdit()
        self.pattern_info.setMaximumHeight(100)
        self.pattern_info.setReadOnly(True)
        info_layout.addWidget(self.pattern_info)
        
        controls_layout.addWidget(info_group)
        
        splitter.addWidget(controls_widget)
        
        # Set splitter proportions (timeline gets most space)
        splitter.setStretchFactor(0, 3)  # Timeline gets 3/4 of space
        splitter.setStretchFactor(1, 1)  # Controls get 1/4 of space
        
        layout.addWidget(splitter)
        
    def setup_connections(self):
        """Setup signal connections between components."""
        # Transport control connections
        self.transport.play_clicked.connect(self.start_practice)
        self.transport.pause_clicked.connect(self.pause_practice)
        self.transport.stop_clicked.connect(self.stop_practice)
        self.transport.bpm_changed.connect(self.on_bpm_changed)
        self.transport.pattern_changed.connect(self.on_pattern_changed)
        
        # Audio control connections
        self.transport.volume_changed.connect(self.on_volume_changed)
        
        # Metronome connections
        self.metronome.tick.connect(self.on_metronome_tick)
        self.metronome.started.connect(self.on_metronome_started)
        self.metronome.stopped.connect(self.on_metronome_stopped)
        
        # Timeline connections
        self.timeline.step_hit.connect(self.on_step_hit)
        
    def set_pattern(self, pattern):
        """Set the current practice pattern."""
        self.current_pattern = pattern
        if pattern:
            # Update UI components
            self.pattern_title.setText(pattern.name)
            self.timeline.set_pattern(pattern)
            self.steps_preview.set_pattern(pattern)
            
            # Update transport controls
            self.transport.set_bpm_range(pattern.bpm_min, pattern.bpm_max)
            self.transport.set_bpm(pattern.bpm_default)
            
            # Update pattern info
            self.update_pattern_info()
            
            # Configure metronome for this pattern
            beats_per_bar = pattern.time_sig[0]
            self.metronome.steps_per_beat = pattern.steps_per_bar // beats_per_bar
            self.metronome.set_bpm(pattern.bpm_default)
            
    def set_patterns(self, patterns):
        """Set available patterns for selection."""
        self.patterns = patterns
        self.transport.set_patterns(patterns)
        
    def update_pattern_info(self):
        """Update the pattern information display."""
        if not self.current_pattern:
            self.pattern_info.setText("Ритм не выбран")
            return
            
        pattern = self.current_pattern
        time_sig = f"{pattern.time_sig[0]}/{pattern.time_sig[1]}"
        bpm_range = f"{pattern.bpm_min}-{pattern.bpm_max} BPM"
        
        info_text = f"""
<b>Ритм:</b> {pattern.name}<br>
<b>Размер:</b> {time_sig}<br>
<b>Шагов в такте:</b> {pattern.steps_per_bar}<br>
<b>Диапазон темпа:</b> {bpm_range}<br>
<b>Рекомендуемый темп:</b> {pattern.bpm_default} BPM<br><br>
<b>Описание:</b><br>
{pattern.notes}
        """.strip()
        
        self.pattern_info.setHtml(info_text)
        
    def start_practice(self):
        """Start practice session."""
        if not self.current_pattern:
            return
            
        # Configure metronome callback for audio/visual feedback
        self.metronome.set_callback(self.on_practice_tick)
        self.metronome.start()
        
    def pause_practice(self):
        """Pause practice session."""
        self.metronome.pause()
        
    def stop_practice(self):
        """Stop practice session."""
        self.metronome.stop()
        self.timeline.set_current_step(0)
        self.steps_preview.set_current_step(0)
        
    def on_bpm_changed(self, bpm: int):
        """Handle BPM change from transport controls."""
        self.metronome.set_bpm(bpm)
        
    def on_pattern_changed(self, pattern_id: str):
        """Handle pattern change from transport controls."""
        if pattern_id and pattern_id in self.patterns:
            # Get the new pattern
            new_pattern = self.patterns[pattern_id]
            
            # Update current pattern
            self.current_pattern = new_pattern
            
            # Update UI components with new pattern
            self.pattern_title.setText(new_pattern.name)
            self.timeline.set_pattern(new_pattern)
            self.steps_preview.set_pattern(new_pattern)
            
            # Update pattern info display
            self.update_pattern_info()
            
            # Configure metronome for the new pattern
            beats_per_bar = new_pattern.time_sig[0]
            self.metronome.steps_per_beat = new_pattern.steps_per_bar // beats_per_bar
            
            # Reset timeline position when pattern changes
            self.timeline.set_current_step(0)
            self.steps_preview.set_current_step(0)
        
    def on_volume_changed(self, volume_type: str, value: float):
        """Handle volume changes from transport controls."""
        if volume_type == 'master':
            self.audio.set_volumes(master=value)
        elif volume_type == 'click':
            self.audio.set_volumes(click=value)
        elif volume_type == 'strum':
            self.audio.set_volumes(strum=value)
        
    def on_metronome_tick(self, timestamp: float, step_index: int):
        """Handle metronome tick for GUI updates (Qt signal, thread-safe)."""
        if not self.current_pattern:
            return
            
        # Update timeline visualization
        self.timeline.set_current_step(step_index)
        self.steps_preview.set_current_step(step_index)
        
    def on_practice_tick(self, timestamp: float, step_index: int):
        """Handle metronome tick for audio feedback (callback)."""
        if not self.current_pattern:
            return
            
        bar_length = self.current_pattern.steps_per_bar
        bar_step = step_index % bar_length
        
        # Play audio feedback
        if bar_step < len(self.current_pattern.steps):
            step = self.current_pattern.steps[bar_step]
            
            # Play strum sound
            if step.dir != "-":
                self.audio.play_strum(step.dir, step.accent)
            
            # Play metronome click with beat awareness
            beats_per_bar = self.current_pattern.time_sig[0]
            steps_per_beat = bar_length // beats_per_bar
            
            if bar_step == 0:
                # Strong beat (downbeat) - use high click
                self.audio.play_click_high()
            elif bar_step % steps_per_beat == 0:
                # Other beats - use accented click
                self.audio.play_click(accent=True)
            # No click on off-beats for cleaner sound
                
    def on_metronome_started(self):
        """Handle metronome start."""
        self.transport.set_playing(True)
        
    def on_metronome_stopped(self):
        """Handle metronome stop."""
        self.transport.set_playing(False)
        
    def on_step_hit(self, step_index: int):
        """Handle step hit from timeline widget."""
        # Could be used for user interaction feedback
        pass
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for better UX."""
        # Play/Pause - Space bar
        self.play_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.play_shortcut.activated.connect(self.transport.on_play_pause_clicked)
        
        # Stop - Escape
        self.stop_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.stop_shortcut.activated.connect(self.transport.on_stop_clicked)
        
        # BPM adjustment
        self.bpm_up_shortcut = QShortcut(QKeySequence(Qt.Key_Plus), self)
        self.bpm_up_shortcut.activated.connect(lambda: self.transport.adjust_bpm(5))
        
        self.bpm_down_shortcut = QShortcut(QKeySequence(Qt.Key_Minus), self)
        self.bpm_down_shortcut.activated.connect(lambda: self.transport.adjust_bpm(-5))
        
        # Back to menu - Alt+Left
        self.back_shortcut = QShortcut(QKeySequence(Qt.ALT | Qt.Key_Left), self)
        self.back_shortcut.activated.connect(self.back_requested.emit)
        
    def cleanup(self):
        """Cleanup when view is closed."""
        self.metronome.stop()
