#!/usr/bin/env python3
"""
Test script to demonstrate audio controls functionality.
Shows how the mute buttons and enable/disable checkboxes work.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from ui.components.volume_controls import VolumeControls
from core.audio_engine import AudioEngine


class AudioControlsTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Controls Test - GStrummer")
        self.setGeometry(100, 100, 600, 400)
        
        # Initialize audio engine
        self.audio_engine = AudioEngine()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("🎸 Audio Controls Test")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Add volume controls
        self.volume_controls = VolumeControls()
        layout.addWidget(self.volume_controls)
        
        # Add status label
        self.status_label = QLabel("Ready - Try the controls above!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; margin: 20px;")
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.setup_connections()
        
    def setup_connections(self):
        """Connect volume controls to audio engine."""
        self.volume_controls.volume_changed.connect(self.on_volume_changed)
        self.volume_controls.enabled_changed.connect(self.on_enabled_changed)
        
    def on_volume_changed(self, volume_type: str, value: float):
        """Handle volume changes."""
        self.audio_engine.set_volumes(**{volume_type: value})
        self.status_label.setText(f"Volume changed: {volume_type} = {int(value*100)}%")
        
        # Play test sound
        if volume_type == 'click':
            self.audio_engine.play_click()
        elif volume_type == 'strum':
            self.audio_engine.play_strum('D', 0.5)
            
    def on_enabled_changed(self, audio_type: str, enabled: bool):
        """Handle enable/disable changes."""
        if audio_type == 'click':
            self.audio_engine.set_click_enabled(enabled)
            status = "enabled" if enabled else "disabled"
            self.status_label.setText(f"Metronome {status}")
            # Test click
            self.audio_engine.play_click()
        elif audio_type == 'strum':
            self.audio_engine.set_strum_enabled(enabled)
            status = "enabled" if enabled else "disabled" 
            self.status_label.setText(f"Strum sounds {status}")
            # Test strum
            self.audio_engine.play_strum('D', 0.5)


def main():
    app = QApplication(sys.argv)
    
    window = AudioControlsTestWindow()
    window.show()
    
    print("🎸 Audio Controls Test Window")
    print("=" * 40)
    print("Controls available:")
    print("• Volume sliders - adjust volume levels")
    print("• Mute buttons (🔊/🔇) - toggle volume on/off")
    print("• Enable checkboxes - enable/disable audio types")
    print("")
    print("Test the controls to see status updates!")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())