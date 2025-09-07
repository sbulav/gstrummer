from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QToolTip)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class AudioStatusBar(QWidget):
    """Compact audio status bar with icon indicators and settings popup."""
    
    # Signals for audio state changes
    volume_changed = Signal(str, float)  # volume_type, value
    enabled_changed = Signal(str, bool)  # audio_type, enabled
    mute_toggled = Signal(str, bool)     # volume_type, muted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Audio state tracking
        self._master_muted = False
        self._master_volume = 0.8
        self._click_enabled = True
        self._click_muted = False
        self._click_volume = 0.7
        self._strum_enabled = True
        self._strum_muted = False
        self._strum_volume = 0.5
        
        # Popup window (created on demand)
        self._settings_popup = None
        
        self.init_ui()
        self.update_icon_states()
        
    def init_ui(self):
        """Initialize the compact status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        # Master volume status
        self.master_btn = QPushButton("🔊")
        self.master_btn.setMinimumSize(35, 35)
        self.master_btn.setMaximumSize(45, 45)
        self.master_btn.setCheckable(True)
        self.master_btn.setToolTip("Master Volume (Click to mute/unmute)")
        self.master_btn.clicked.connect(self._toggle_master_mute)
        layout.addWidget(self.master_btn)
        
        # Metronome status  
        self.click_btn = QPushButton("🎵")
        self.click_btn.setMinimumSize(35, 35)
        self.click_btn.setMaximumSize(45, 45)
        self.click_btn.setCheckable(True)
        self.click_btn.setToolTip("Metronome (Click to enable/disable)")
        self.click_btn.clicked.connect(self._toggle_click_enabled)
        layout.addWidget(self.click_btn)
        
        # Strum sounds status
        self.strum_btn = QPushButton("🎸")
        self.strum_btn.setMinimumSize(35, 35)
        self.strum_btn.setMaximumSize(45, 45)
        self.strum_btn.setCheckable(True)
        self.strum_btn.setToolTip("Strum Sounds (Click to enable/disable)")
        self.strum_btn.clicked.connect(self._toggle_strum_enabled)
        layout.addWidget(self.strum_btn)
        
        # Settings button
        self.settings_btn = QPushButton("🔧")
        self.settings_btn.setMinimumSize(35, 35)
        self.settings_btn.setMaximumSize(45, 45)
        self.settings_btn.setToolTip("Audio Settings (Click for detailed controls)")
        self.settings_btn.clicked.connect(self._open_settings_popup)
        layout.addWidget(self.settings_btn)
        
        # Add stretch to keep icons compact
        layout.addStretch()
        
        # Style the buttons
        self._apply_button_styles()
        
    def _apply_button_styles(self):
        """Apply consistent styling to all buttons."""
        button_style = """
        QPushButton {
            border: 1px solid #bdc3c7;
            border-radius: 6px;
            background-color: #ecf0f1;
            font-size: 16px;
            font-weight: bold;
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
        """
        
        for btn in [self.master_btn, self.click_btn, self.strum_btn]:
            btn.setStyleSheet(button_style)
            
        # Settings button has different style
        settings_style = """
        QPushButton {
            border: 1px solid #95a5a6;
            border-radius: 6px;
            background-color: #f8f9fa;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #e9ecef;
            border: 2px solid #6c757d;
        }
        QPushButton:pressed {
            background-color: #dee2e6;
        }
        """
        self.settings_btn.setStyleSheet(settings_style)
        
    def update_icon_states(self):
        """Update icon display based on current audio states."""
        # Master volume icon
        if self._master_muted or self._master_volume == 0:
            self.master_btn.setText("🔇")
            self.master_btn.setChecked(True)
            self.master_btn.setToolTip(f"Master Volume: MUTED ({int(self._master_volume * 100)}%)")
        else:
            self.master_btn.setText("🔊")
            self.master_btn.setChecked(False)
            self.master_btn.setToolTip(f"Master Volume: {int(self._master_volume * 100)}%")
            
        # Metronome icon
        if not self._click_enabled or self._click_muted:
            self.click_btn.setText("🔇")
            self.click_btn.setChecked(True)
            if not self._click_enabled:
                self.click_btn.setToolTip(f"Metronome: DISABLED")
            else:
                self.click_btn.setToolTip(f"Metronome: MUTED ({int(self._click_volume * 100)}%)")
        else:
            self.click_btn.setText("🎵")
            self.click_btn.setChecked(False)
            self.click_btn.setToolTip(f"Metronome: {int(self._click_volume * 100)}%")
            
        # Strum sounds icon
        if not self._strum_enabled or self._strum_muted:
            self.strum_btn.setText("🔇")
            self.strum_btn.setChecked(True)
            if not self._strum_enabled:
                self.strum_btn.setToolTip(f"Strum Sounds: DISABLED")
            else:
                self.strum_btn.setToolTip(f"Strum Sounds: MUTED ({int(self._strum_volume * 100)}%)")
        else:
            self.strum_btn.setText("🎸")
            self.strum_btn.setChecked(False)
            self.strum_btn.setToolTip(f"Strum Sounds: {int(self._strum_volume * 100)}%")
            
    def _toggle_master_mute(self):
        """Toggle master volume mute state."""
        self._master_muted = not self._master_muted
        self.update_icon_states()
        
        # Emit signal with effective volume (0 if muted)
        effective_volume = 0.0 if self._master_muted else self._master_volume
        self.volume_changed.emit('master', effective_volume)
        self.mute_toggled.emit('master', self._master_muted)
        
    def _toggle_click_enabled(self):
        """Toggle metronome enabled state."""
        self._click_enabled = not self._click_enabled
        self.update_icon_states()
        self.enabled_changed.emit('click', self._click_enabled)
        
    def _toggle_strum_enabled(self):
        """Toggle strum sounds enabled state."""
        self._strum_enabled = not self._strum_enabled
        self.update_icon_states()
        self.enabled_changed.emit('strum', self._strum_enabled)
        
    def _open_settings_popup(self):
        """Open the detailed audio settings popup."""
        if self._settings_popup is None:
            from .audio_settings_popup import AudioSettingsPopup
            self._settings_popup = AudioSettingsPopup(self)
            
            # Connect popup signals to our signals
            self._settings_popup.volume_changed.connect(self._on_popup_volume_changed)
            self._settings_popup.enabled_changed.connect(self._on_popup_enabled_changed)
            self._settings_popup.mute_toggled.connect(self._on_popup_mute_toggled)
            
        # Update popup with current values  
        if self._settings_popup:
            self._settings_popup.set_master_volume(self._master_volume, self._master_muted)
            self._settings_popup.set_click_volume(self._click_volume, self._click_muted, self._click_enabled)
            self._settings_popup.set_strum_volume(self._strum_volume, self._strum_muted, self._strum_enabled)
        
        # Show popup
        self._settings_popup.show()
        self._settings_popup.raise_()
        self._settings_popup.activateWindow()
        
    def _on_popup_volume_changed(self, volume_type: str, value: float):
        """Handle volume changes from popup."""
        if volume_type == 'master':
            self._master_volume = value
        elif volume_type == 'click':
            self._click_volume = value
        elif volume_type == 'strum':
            self._strum_volume = value
            
        self.update_icon_states()
        self.volume_changed.emit(volume_type, value)
        
    def _on_popup_enabled_changed(self, audio_type: str, enabled: bool):
        """Handle enable/disable changes from popup."""
        if audio_type == 'click':
            self._click_enabled = enabled
        elif audio_type == 'strum':
            self._strum_enabled = enabled
            
        self.update_icon_states()
        self.enabled_changed.emit(audio_type, enabled)
        
    def _on_popup_mute_toggled(self, volume_type: str, muted: bool):
        """Handle mute toggle from popup."""
        if volume_type == 'master':
            self._master_muted = muted
        elif volume_type == 'click':
            self._click_muted = muted
        elif volume_type == 'strum':
            self._strum_muted = muted
            
        self.update_icon_states()
        self.mute_toggled.emit(volume_type, muted)
        
        # Also emit volume signal with effective volume
        if volume_type == 'master':
            effective_volume = 0.0 if muted else self._master_volume
        elif volume_type == 'click':
            effective_volume = 0.0 if muted else self._click_volume
        elif volume_type == 'strum':
            effective_volume = 0.0 if muted else self._strum_volume
        else:
            return
            
        self.volume_changed.emit(volume_type, effective_volume)
        
    # Public methods for external state updates
    def set_master_volume(self, volume: float, muted: bool = None):
        """Set master volume and optionally mute state."""
        self._master_volume = max(0.0, min(1.0, volume))
        if muted is not None:
            self._master_muted = muted
        self.update_icon_states()
        
    def set_click_volume(self, volume: float, muted: bool = None, enabled: bool = None):
        """Set click volume and optionally mute/enable state."""
        self._click_volume = max(0.0, min(1.0, volume))
        if muted is not None:
            self._click_muted = muted
        if enabled is not None:
            self._click_enabled = enabled
        self.update_icon_states()
        
    def set_strum_volume(self, volume: float, muted: bool = None, enabled: bool = None):
        """Set strum volume and optionally mute/enable state."""
        self._strum_volume = max(0.0, min(1.0, volume))
        if muted is not None:
            self._strum_muted = muted
        if enabled is not None:
            self._strum_enabled = enabled
        self.update_icon_states()
        
    def get_audio_states(self) -> dict:
        """Get current audio states for debugging."""
        return {
            'master': {'volume': self._master_volume, 'muted': self._master_muted},
            'click': {'volume': self._click_volume, 'muted': self._click_muted, 'enabled': self._click_enabled},
            'strum': {'volume': self._strum_volume, 'muted': self._strum_muted, 'enabled': self._strum_enabled}
        }