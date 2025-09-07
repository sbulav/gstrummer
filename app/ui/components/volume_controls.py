from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSlider, QPushButton, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class VolumeControls(QWidget):
    """Volume control widget with sliders for different audio types."""
    
    volume_changed = Signal(str, float)  # volume_type, value
    mute_toggled = Signal(str, bool)     # volume_type, muted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Mute states
        self._click_muted = False
        self._strum_muted = False
        self._master_muted = False
        
    def init_ui(self):
        """Initialize the volume controls UI."""
        layout = QVBoxLayout(self)
        
        # Master volume
        master_group = QGroupBox("🔊 Основная громкость")
        master_layout = QHBoxLayout(master_group)
        
        self.master_slider = QSlider(Qt.Orientation.Horizontal)
        self.master_slider.setRange(0, 100)
        self.master_slider.setValue(80)
        self.master_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit('master', v / 100.0)
        )
        
        self.master_label = QLabel("80%")
        self.master_label.setMinimumWidth(35)
        self.master_slider.valueChanged.connect(
            lambda v: self.master_label.setText(f"{v}%")
        )
        
        self.master_mute = QPushButton("🔊")
        self.master_mute.setMaximumWidth(40)
        self.master_mute.setCheckable(True)
        self.master_mute.toggled.connect(
            lambda checked: self._toggle_mute('master', checked)
        )
        
        master_layout.addWidget(self.master_slider)
        master_layout.addWidget(self.master_label)
        master_layout.addWidget(self.master_mute)
        
        layout.addWidget(master_group)
        
        # Click and Strum controls in horizontal layout
        controls_layout = QHBoxLayout()
        
        # Click volume
        click_group = QGroupBox("🎵 Метроном")
        click_layout = QVBoxLayout(click_group)
        
        click_controls = QHBoxLayout()
        self.click_slider = QSlider(Qt.Orientation.Horizontal)
        self.click_slider.setRange(0, 100)
        self.click_slider.setValue(70)
        self.click_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit('click', v / 100.0)
        )
        
        self.click_label = QLabel("70%")
        self.click_label.setMinimumWidth(35)
        self.click_slider.valueChanged.connect(
            lambda v: self.click_label.setText(f"{v}%")
        )
        
        self.click_mute = QPushButton("🎵")
        self.click_mute.setMaximumWidth(40)
        self.click_mute.setCheckable(True)
        self.click_mute.toggled.connect(
            lambda checked: self._toggle_mute('click', checked)
        )
        
        click_controls.addWidget(self.click_slider)
        click_controls.addWidget(self.click_label)
        click_controls.addWidget(self.click_mute)
        click_layout.addLayout(click_controls)
        
        controls_layout.addWidget(click_group)
        
        # Strum volume
        strum_group = QGroupBox("🎸 Бой")
        strum_layout = QVBoxLayout(strum_group)
        
        strum_controls = QHBoxLayout()
        self.strum_slider = QSlider(Qt.Orientation.Horizontal)
        self.strum_slider.setRange(0, 100)
        self.strum_slider.setValue(50)
        self.strum_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit('strum', v / 100.0)
        )
        
        self.strum_label = QLabel("50%")
        self.strum_label.setMinimumWidth(35)
        self.strum_slider.valueChanged.connect(
            lambda v: self.strum_label.setText(f"{v}%")
        )
        
        self.strum_mute = QPushButton("🎸")
        self.strum_mute.setMaximumWidth(40)
        self.strum_mute.setCheckable(True)
        self.strum_mute.toggled.connect(
            lambda checked: self._toggle_mute('strum', checked)
        )
        
        strum_controls.addWidget(self.strum_slider)
        strum_controls.addWidget(self.strum_label)
        strum_controls.addWidget(self.strum_mute)
        strum_layout.addLayout(strum_controls)
        
        controls_layout.addWidget(strum_group)
        
        layout.addLayout(controls_layout)
        
    def _toggle_mute(self, volume_type: str, muted: bool):
        """Handle mute toggle for different volume types."""
        if volume_type == 'master':
            self._master_muted = muted
            self.master_mute.setText("🔇" if muted else "🔊")
            # Mute by setting volume to 0
            volume = 0.0 if muted else self.master_slider.value() / 100.0
        elif volume_type == 'click':
            self._click_muted = muted
            self.click_mute.setText("🔇" if muted else "🎵")
            volume = 0.0 if muted else self.click_slider.value() / 100.0
        elif volume_type == 'strum':
            self._strum_muted = muted
            self.strum_mute.setText("🔇" if muted else "🎸")
            volume = 0.0 if muted else self.strum_slider.value() / 100.0
        else:
            return
            
        self.volume_changed.emit(volume_type, volume)
        
    def set_volume(self, volume_type: str, value: float):
        """Set volume slider value (0.0 to 1.0)."""
        int_value = int(value * 100)
        
        if volume_type == 'master':
            self.master_slider.setValue(int_value)
        elif volume_type == 'click':
            self.click_slider.setValue(int_value)
        elif volume_type == 'strum':
            self.strum_slider.setValue(int_value)