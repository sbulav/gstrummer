#!/usr/bin/env python3
"""Test script to verify the display scaling fix for mute buttons."""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QGroupBox)
from PySide6.QtCore import Qt

# Add app to Python path
sys.path.insert(0, 'app')

from ui.components.volume_controls import VolumeControls
from core.audio_engine import AudioEngine


class ScalingTestWindow(QMainWindow):
    """Test window for display scaling fix verification."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Display Scaling Fix Test - GStrummer")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize audio engine for testing
        self.audio_engine = AudioEngine()
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🎵 Display Scaling Fix Verification")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Display info
        app = QApplication.instance()
        screen = app.primaryScreen()
        device_ratio = screen.devicePixelRatio()
        geometry = screen.geometry()
        
        info_text = f"""
Display Information:
• Screen Size: {geometry.width()}x{geometry.height()}
• Device Pixel Ratio: {device_ratio}
• Expected: Mute buttons should now be visible and clickable
• Button sizes increased from 40px to 50-80px range
        """
        
        info_label = QLabel(info_text.strip())
        info_label.setStyleSheet("background: #f8f9fa; padding: 15px; margin: 10px; border: 1px solid #dee2e6; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # Volume controls test
        controls_group = QGroupBox("🔊 Fixed Volume Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.volume_controls = VolumeControls()
        controls_layout.addWidget(self.volume_controls)
        layout.addWidget(controls_group)
        
        # Test buttons
        test_group = QGroupBox("🧪 Audio Tests")
        test_layout = QHBoxLayout(test_group)
        
        test_click_btn = QPushButton("🎵 Test Click")
        test_click_btn.clicked.connect(self.test_click)
        test_click_btn.setMinimumHeight(40)
        test_layout.addWidget(test_click_btn)
        
        test_strum_btn = QPushButton("🎸 Test Strum")
        test_strum_btn.clicked.connect(self.test_strum)
        test_strum_btn.setMinimumHeight(40)
        test_layout.addWidget(test_strum_btn)
        
        layout.addWidget(test_group)
        
        # Instructions
        instructions = QLabel("""
Instructions for Testing:
1. ✅ Check that all mute buttons (🔊🔇, 🎵🔇, 🎸🔇) are VISIBLE
2. ✅ Check that all mute buttons are CLICKABLE (should toggle icon)
3. ✅ Check that volume sliders work smoothly
4. ✅ Check that enable/disable checkboxes are functional
5. ✅ Test audio with the buttons above (if system audio works)
        """)
        instructions.setStyleSheet("background: #d4edda; padding: 15px; margin: 10px; border: 1px solid #c3e6cb; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Status
        self.status_label = QLabel("Ready for testing - interact with controls above")
        self.status_label.setStyleSheet("margin: 10px; padding: 10px; background: #cce5ff; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
    def setup_connections(self):
        # Connect volume controls signals
        self.volume_controls.volume_changed.connect(self.on_volume_changed)
        self.volume_controls.enabled_changed.connect(self.on_enabled_changed)
        self.volume_controls.mute_toggled.connect(self.on_mute_toggled)
        
    def on_volume_changed(self, volume_type: str, value: float):
        self.status_label.setText(f"✅ Volume changed: {volume_type} = {value:.2f}")
        
        if volume_type == 'master':
            self.audio_engine.set_volumes(master=value)
        elif volume_type == 'click':
            self.audio_engine.set_volumes(click=value)
        elif volume_type == 'strum':
            self.audio_engine.set_volumes(strum=value)
            
    def on_enabled_changed(self, audio_type: str, enabled: bool):
        self.status_label.setText(f"✅ Enable/disable: {audio_type} = {'ON' if enabled else 'OFF'}")
        
        if audio_type == 'click':
            self.audio_engine.set_click_enabled(enabled)
        elif audio_type == 'strum':
            self.audio_engine.set_strum_enabled(enabled)
            
    def on_mute_toggled(self, volume_type: str, muted: bool):
        self.status_label.setText(f"✅ Mute toggled: {volume_type} = {'MUTED' if muted else 'UNMUTED'}")
        
    def test_click(self):
        self.audio_engine.play_click_high()
        self.status_label.setText("🎵 Played click sound (if audio enabled)")
        
    def test_strum(self):
        self.audio_engine.play_strum("D", 1.0)
        self.status_label.setText("🎸 Played strum sound (if audio enabled)")
        
    def closeEvent(self, event):
        self.audio_engine.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    window = ScalingTestWindow()
    window.show()
    
    print("="*60)
    print("DISPLAY SCALING FIX TEST")
    print("="*60)
    print("1. Check that ALL mute buttons are visible")
    print("2. Check that ALL mute buttons are clickable") 
    print("3. Test volume sliders and checkboxes")
    print("4. Close window or press Ctrl+C when done")
    print("="*60)
    
    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\nTest completed by user")
        return 0
    finally:
        if 'window' in locals():
            window.close()


if __name__ == "__main__":
    sys.exit(main())
