from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSlider, QPushButton, QCheckBox, QGroupBox,
                               QDialogButtonBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class AudioSettingsPopup(QDialog):
    """Popup window with detailed audio settings controls."""
    
    # Signals for audio state changes
    volume_changed = Signal(str, float)  # volume_type, value
    enabled_changed = Signal(str, bool)  # audio_type, enabled
    mute_toggled = Signal(str, bool)     # volume_type, muted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Audio state
        self._master_volume = 0.8
        self._master_muted = False
        self._click_volume = 0.7
        self._click_muted = False
        self._click_enabled = True
        self._strum_volume = 0.5
        self._strum_muted = False
        self._strum_enabled = True
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the popup dialog UI."""
        self.setWindowTitle("Audio Settings - GStrummer")
        self.setModal(True)
        self.setFixedSize(450, 350)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔊 Audio Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Master volume section
        master_group = self._create_master_volume_section()
        layout.addWidget(master_group)
        
        # Metronome section  
        click_group = self._create_click_volume_section()
        layout.addWidget(click_group)
        
        # Strum sounds section
        strum_group = self._create_strum_volume_section()
        layout.addWidget(strum_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        
        # Apply styling
        self.setStyleSheet(self._get_dialog_stylesheet())
        
    def _create_master_volume_section(self):
        """Create master volume controls section."""
        group = QGroupBox("🔊 Master Volume")
        layout = QVBoxLayout(group)
        
        # Volume control row
        volume_layout = QHBoxLayout()
        
        self.master_slider = QSlider(Qt.Orientation.Horizontal)
        self.master_slider.setRange(0, 100)
        self.master_slider.setValue(int(self._master_volume * 100))
        volume_layout.addWidget(self.master_slider)
        
        self.master_label = QLabel(f"{int(self._master_volume * 100)}%")
        self.master_label.setMinimumWidth(40)
        self.master_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(self.master_label)
        
        self.master_mute_btn = QPushButton("🔊")
        self.master_mute_btn.setCheckable(True)
        self.master_mute_btn.setMaximumWidth(50)
        volume_layout.addWidget(self.master_mute_btn)
        
        layout.addLayout(volume_layout)
        
        return group
        
    def _create_click_volume_section(self):
        """Create metronome volume controls section."""
        group = QGroupBox("🎵 Metronome")
        layout = QVBoxLayout(group)
        
        # Enable checkbox
        self.click_enable_cb = QCheckBox("Enable metronome sounds")
        self.click_enable_cb.setChecked(self._click_enabled)
        layout.addWidget(self.click_enable_cb)
        
        # Volume control row
        volume_layout = QHBoxLayout()
        
        self.click_slider = QSlider(Qt.Orientation.Horizontal)
        self.click_slider.setRange(0, 100)
        self.click_slider.setValue(int(self._click_volume * 100))
        volume_layout.addWidget(self.click_slider)
        
        self.click_label = QLabel(f"{int(self._click_volume * 100)}%")
        self.click_label.setMinimumWidth(40)
        self.click_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(self.click_label)
        
        self.click_mute_btn = QPushButton("🎵")
        self.click_mute_btn.setCheckable(True)
        self.click_mute_btn.setMaximumWidth(50)
        volume_layout.addWidget(self.click_mute_btn)
        
        layout.addLayout(volume_layout)
        
        return group
        
    def _create_strum_volume_section(self):
        """Create strum sounds volume controls section."""
        group = QGroupBox("🎸 Strum Sounds")
        layout = QVBoxLayout(group)
        
        # Enable checkbox
        self.strum_enable_cb = QCheckBox("Enable strum sounds")
        self.strum_enable_cb.setChecked(self._strum_enabled)
        layout.addWidget(self.strum_enable_cb)
        
        # Volume control row
        volume_layout = QHBoxLayout()
        
        self.strum_slider = QSlider(Qt.Orientation.Horizontal)
        self.strum_slider.setRange(0, 100)
        self.strum_slider.setValue(int(self._strum_volume * 100))
        volume_layout.addWidget(self.strum_slider)
        
        self.strum_label = QLabel(f"{int(self._strum_volume * 100)}%")
        self.strum_label.setMinimumWidth(40)
        self.strum_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(self.strum_label)
        
        self.strum_mute_btn = QPushButton("🎸")
        self.strum_mute_btn.setCheckable(True)
        self.strum_mute_btn.setMaximumWidth(50)
        volume_layout.addWidget(self.strum_mute_btn)
        
        layout.addLayout(volume_layout)
        
        return group
        
    def setup_connections(self):
        """Setup signal connections for all controls."""
        # Master volume connections
        self.master_slider.valueChanged.connect(self._on_master_volume_changed)
        self.master_mute_btn.toggled.connect(self._on_master_mute_toggled)
        
        # Click volume connections
        self.click_enable_cb.toggled.connect(self._on_click_enabled_changed)
        self.click_slider.valueChanged.connect(self._on_click_volume_changed)
        self.click_mute_btn.toggled.connect(self._on_click_mute_toggled)
        
        # Strum volume connections
        self.strum_enable_cb.toggled.connect(self._on_strum_enabled_changed)
        self.strum_slider.valueChanged.connect(self._on_strum_volume_changed)
        self.strum_mute_btn.toggled.connect(self._on_strum_mute_toggled)
        
    def _on_master_volume_changed(self, value: int):
        """Handle master volume slider change."""
        self._master_volume = value / 100.0
        self.master_label.setText(f"{value}%")
        
        # Only emit if not muted
        if not self._master_muted:
            self.volume_changed.emit('master', self._master_volume)
        
    def _on_master_mute_toggled(self, checked: bool):
        """Handle master mute button toggle."""
        self._master_muted = checked
        self.master_mute_btn.setText("🔇" if checked else "🔊")
        self.mute_toggled.emit('master', checked)
        
        # Emit volume with 0 if muted, normal volume if unmuted
        effective_volume = 0.0 if checked else self._master_volume
        self.volume_changed.emit('master', effective_volume)
        
    def _on_click_enabled_changed(self, checked: bool):
        """Handle click enable checkbox change."""
        self._click_enabled = checked
        # Enable/disable click volume controls
        self.click_slider.setEnabled(checked)
        self.click_mute_btn.setEnabled(checked)
        self.enabled_changed.emit('click', checked)
        
    def _on_click_volume_changed(self, value: int):
        """Handle click volume slider change."""
        self._click_volume = value / 100.0
        self.click_label.setText(f"{value}%")
        
        # Only emit if enabled and not muted
        if self._click_enabled and not self._click_muted:
            self.volume_changed.emit('click', self._click_volume)
        
    def _on_click_mute_toggled(self, checked: bool):
        """Handle click mute button toggle."""
        self._click_muted = checked
        self.click_mute_btn.setText("🔇" if checked else "🎵")
        self.mute_toggled.emit('click', checked)
        
        # Emit volume with 0 if muted, normal volume if unmuted
        if self._click_enabled:
            effective_volume = 0.0 if checked else self._click_volume
            self.volume_changed.emit('click', effective_volume)
        
    def _on_strum_enabled_changed(self, checked: bool):
        """Handle strum enable checkbox change."""
        self._strum_enabled = checked
        # Enable/disable strum volume controls
        self.strum_slider.setEnabled(checked)
        self.strum_mute_btn.setEnabled(checked)
        self.enabled_changed.emit('strum', checked)
        
    def _on_strum_volume_changed(self, value: int):
        """Handle strum volume slider change."""
        self._strum_volume = value / 100.0
        self.strum_label.setText(f"{value}%")
        
        # Only emit if enabled and not muted
        if self._strum_enabled and not self._strum_muted:
            self.volume_changed.emit('strum', self._strum_volume)
        
    def _on_strum_mute_toggled(self, checked: bool):
        """Handle strum mute button toggle."""
        self._strum_muted = checked
        self.strum_mute_btn.setText("🔇" if checked else "🎸")
        self.mute_toggled.emit('strum', checked)
        
        # Emit volume with 0 if muted, normal volume if unmuted
        if self._strum_enabled:
            effective_volume = 0.0 if checked else self._strum_volume
            self.volume_changed.emit('strum', effective_volume)
        
    def _get_dialog_stylesheet(self):
        """Get stylesheet for the dialog."""
        return """
        QDialog {
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
        
        QSlider::groove:horizontal {
            border: 1px solid #bdc3c7;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #3498db;
            border: 1px solid #2980b9;
            width: 18px;
            height: 16px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #2980b9;
        }
        
        QSlider::sub-page:horizontal {
            background: #3498db;
            border-radius: 4px;
        }
        
        QPushButton {
            border: 1px solid #bdc3c7;
            border-radius: 6px;
            background-color: #ecf0f1;
            padding: 5px 10px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #d5dbdb;
            border: 2px solid #3498db;
        }
        
        QPushButton:pressed {
            background-color: #bdc3c7;
        }
        
        QPushButton:checked {
            background-color: #e74c3c;
            border: 2px solid #c0392b;
            color: white;
        }
        
        QCheckBox {
            font-size: 12px;
            color: #2c3e50;
            spacing: 5px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #bdc3c7;
            background-color: white;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #27ae60;
            background-color: #2ecc71;
            border-radius: 3px;
        }
        
        QLabel {
            color: #2c3e50;
        }
        """
        
    # Public methods for setting values from parent
    def set_master_volume(self, volume: float, muted: bool):
        """Set master volume values."""
        self._master_volume = volume
        self._master_muted = muted
        
        self.master_slider.setValue(int(volume * 100))
        self.master_label.setText(f"{int(volume * 100)}%")
        self.master_mute_btn.setChecked(muted)
        self.master_mute_btn.setText("🔇" if muted else "🔊")
        
    def set_click_volume(self, volume: float, muted: bool, enabled: bool):
        """Set click volume values."""
        self._click_volume = volume
        self._click_muted = muted  
        self._click_enabled = enabled
        
        self.click_slider.setValue(int(volume * 100))
        self.click_slider.setEnabled(enabled)
        self.click_label.setText(f"{int(volume * 100)}%")
        self.click_mute_btn.setChecked(muted)
        self.click_mute_btn.setText("🔇" if muted else "🎵")
        self.click_mute_btn.setEnabled(enabled)
        self.click_enable_cb.setChecked(enabled)
        
    def set_strum_volume(self, volume: float, muted: bool, enabled: bool):
        """Set strum volume values."""
        self._strum_volume = volume
        self._strum_muted = muted
        self._strum_enabled = enabled
        
        self.strum_slider.setValue(int(volume * 100))
        self.strum_slider.setEnabled(enabled)
        self.strum_label.setText(f"{int(volume * 100)}%")
        self.strum_mute_btn.setChecked(muted)
        self.strum_mute_btn.setText("🔇" if muted else "🎸")
        self.strum_mute_btn.setEnabled(enabled)
        self.strum_enable_cb.setChecked(enabled)