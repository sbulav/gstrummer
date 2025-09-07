from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QSlider, QLabel, QComboBox, QSpinBox, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont
from typing import Optional, Dict


class TransportControls(QWidget):
    """Transport controls for play/pause/stop and tempo adjustment."""
    
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    bpm_changed = Signal(int)
    pattern_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.current_bpm = 120
        self.bpm_min = 60
        self.bpm_max = 200
        self.patterns = {}
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the transport controls UI."""
        layout = QHBoxLayout(self)
        
        # Playback controls
        playback_group = self.create_playback_controls()
        layout.addWidget(playback_group)
        
        # Tempo controls
        tempo_group = self.create_tempo_controls()
        layout.addWidget(tempo_group)
        
        # Pattern selection
        pattern_group = self.create_pattern_controls()
        layout.addWidget(pattern_group)
        
    def create_playback_controls(self):
        """Create play/pause/stop controls."""
        group = QGroupBox("Воспроизведение")
        layout = QHBoxLayout(group)
        
        # Play/Pause button
        self.play_button = QPushButton("▶ Play")
        self.play_button.setMinimumWidth(80)
        self.play_button.setMinimumHeight(40)
        self.play_button.clicked.connect(self.on_play_pause_clicked)
        layout.addWidget(self.play_button)
        
        # Stop button  
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setMinimumWidth(80)
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        layout.addWidget(self.stop_button)
        
        return group
        
    def create_tempo_controls(self):
        """Create BPM adjustment controls."""
        group = QGroupBox("Темп")
        layout = QVBoxLayout(group)
        
        # BPM display
        bpm_layout = QHBoxLayout()
        self.bpm_label = QLabel(f"{self.current_bpm} BPM")
        self.bpm_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.bpm_label.setAlignment(Qt.AlignCenter)
        bpm_layout.addWidget(self.bpm_label)
        layout.addLayout(bpm_layout)
        
        # BPM slider
        self.bpm_slider = QSlider(Qt.Horizontal)
        self.bpm_slider.setMinimum(self.bpm_min)
        self.bpm_slider.setMaximum(self.bpm_max)
        self.bpm_slider.setValue(self.current_bpm)
        self.bpm_slider.valueChanged.connect(self.on_bpm_slider_changed)
        layout.addWidget(self.bpm_slider)
        
        # BPM adjustment buttons
        bpm_buttons_layout = QHBoxLayout()
        
        self.bpm_down_button = QPushButton("-5")
        self.bpm_down_button.setMaximumWidth(40)
        self.bpm_down_button.clicked.connect(lambda: self.adjust_bpm(-5))
        bpm_buttons_layout.addWidget(self.bpm_down_button)
        
        # BPM spin box
        self.bpm_spinbox = QSpinBox()
        self.bpm_spinbox.setMinimum(self.bpm_min)
        self.bpm_spinbox.setMaximum(self.bpm_max)
        self.bpm_spinbox.setValue(self.current_bpm)
        self.bpm_spinbox.valueChanged.connect(self.on_bpm_spinbox_changed)
        bpm_buttons_layout.addWidget(self.bpm_spinbox)
        
        self.bpm_up_button = QPushButton("+5")
        self.bpm_up_button.setMaximumWidth(40)
        self.bpm_up_button.clicked.connect(lambda: self.adjust_bpm(5))
        bpm_buttons_layout.addWidget(self.bpm_up_button)
        
        layout.addLayout(bpm_buttons_layout)
        
        # BPM range indicator
        range_layout = QHBoxLayout()
        self.bpm_min_label = QLabel(f"{self.bpm_min}")
        self.bpm_max_label = QLabel(f"{self.bpm_max}")
        self.bpm_min_label.setStyleSheet("font-size: 10px; color: gray;")
        self.bpm_max_label.setStyleSheet("font-size: 10px; color: gray;")
        
        range_layout.addWidget(self.bpm_min_label)
        range_layout.addStretch()
        range_layout.addWidget(self.bpm_max_label)
        layout.addLayout(range_layout)
        
        return group
        
    def create_pattern_controls(self):
        """Create pattern selection controls."""
        group = QGroupBox("Ритмический рисунок")
        layout = QVBoxLayout(group)
        
        # Pattern selector
        self.pattern_combo = QComboBox()
        self.pattern_combo.setMinimumWidth(200)
        self.pattern_combo.currentTextChanged.connect(self.on_pattern_changed)
        layout.addWidget(self.pattern_combo)
        
        # Pattern info
        self.pattern_info_label = QLabel("Выберите ритм")
        self.pattern_info_label.setWordWrap(True)
        self.pattern_info_label.setStyleSheet("font-size: 10px; color: gray; margin-top: 5px;")
        layout.addWidget(self.pattern_info_label)
        
        return group
        
    def on_play_pause_clicked(self):
        """Handle play/pause button click."""
        if self.is_playing:
            self.pause_clicked.emit()
            self.set_playing(False)
        else:
            self.play_clicked.emit()
            self.set_playing(True)
            
    def on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_clicked.emit()
        self.set_playing(False)
        
    def set_playing(self, playing: bool):
        """Update playing state and button text."""
        self.is_playing = playing
        if playing:
            self.play_button.setText("⏸ Pause")
            self.play_button.setStyleSheet("background-color: #ffdddd;")
        else:
            self.play_button.setText("▶ Play")
            self.play_button.setStyleSheet("")
            
    def on_bpm_slider_changed(self, value: int):
        """Handle BPM slider change."""
        self.current_bpm = value
        self.update_bpm_displays()
        self.bpm_changed.emit(value)
        
    def on_bpm_spinbox_changed(self, value: int):
        """Handle BPM spinbox change."""
        self.current_bpm = value
        self.bpm_slider.setValue(value)
        self.update_bpm_displays()
        self.bpm_changed.emit(value)
        
    def adjust_bpm(self, delta: int):
        """Adjust BPM by delta amount."""
        new_bpm = max(self.bpm_min, min(self.bpm_max, self.current_bpm + delta))
        self.set_bpm(new_bpm)
        
    def set_bpm(self, bpm: int):
        """Set BPM value."""
        self.current_bpm = max(self.bpm_min, min(self.bpm_max, bpm))
        self.bpm_slider.setValue(self.current_bpm)
        self.bpm_spinbox.setValue(self.current_bpm)
        self.update_bpm_displays()
        self.bpm_changed.emit(self.current_bpm)
        
    def update_bpm_displays(self):
        """Update BPM label and related displays."""
        self.bpm_label.setText(f"{self.current_bpm} BPM")
        
    def set_bpm_range(self, min_bpm: int, max_bpm: int):
        """Set the BPM range for the current pattern."""
        self.bpm_min = min_bpm
        self.bpm_max = max_bpm
        
        self.bpm_slider.setMinimum(min_bpm)
        self.bpm_slider.setMaximum(max_bpm)
        self.bpm_spinbox.setMinimum(min_bpm)
        self.bpm_spinbox.setMaximum(max_bpm)
        
        self.bpm_min_label.setText(f"{min_bpm}")
        self.bpm_max_label.setText(f"{max_bpm}")
        
        # Clamp current BPM to new range
        if self.current_bpm < min_bpm or self.current_bpm > max_bpm:
            clamped_bpm = max(min_bpm, min(max_bpm, self.current_bpm))
            self.set_bpm(clamped_bpm)
            
    def set_patterns(self, patterns: Dict):
        """Set available patterns in the combo box."""
        self.patterns = patterns
        self.pattern_combo.clear()
        
        for pattern_id, pattern in patterns.items():
            self.pattern_combo.addItem(pattern.name, pattern_id)
            
    def on_pattern_changed(self):
        """Handle pattern selection change."""
        pattern_id = self.pattern_combo.currentData()
        if pattern_id and pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            
            # Update BPM range for this pattern
            self.set_bpm_range(pattern.bpm_min, pattern.bpm_max)
            
            # Set default BPM for this pattern
            self.set_bpm(pattern.bpm_default)
            
            # Update pattern info
            time_sig_str = f"{pattern.time_sig[0]}/{pattern.time_sig[1]}"
            info_text = f"{time_sig_str}, {pattern.steps_per_bar} шагов\n{pattern.notes}"
            self.pattern_info_label.setText(info_text)
            
            self.pattern_changed.emit(pattern_id)
            
    def get_current_pattern_id(self) -> Optional[str]:
        """Get the currently selected pattern ID."""
        return self.pattern_combo.currentData()
        
    def select_pattern(self, pattern_id: str):
        """Programmatically select a pattern."""
        for i in range(self.pattern_combo.count()):
            if self.pattern_combo.itemData(i) == pattern_id:
                self.pattern_combo.setCurrentIndex(i)
                break