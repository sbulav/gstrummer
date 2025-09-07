from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AudioStatusWidget(QWidget):
    """Widget showing audio system status."""
    
    def __init__(self, audio_engine, parent=None):
        super().__init__(parent)
        self.audio = audio_engine
        self.init_ui()
        self.update_status()
        
    def init_ui(self):
        """Initialize the audio status UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def update_status(self):
        """Update the audio status display."""
        if self.audio.is_available():
            device_info = self.audio.get_device_info()
            if device_info and hasattr(device_info, 'get'):
                device_name = device_info.get('name', 'Unknown')
            else:
                device_name = "Available"
            self.status_label.setText(f"🔊 Audio: {device_name}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("🔇 Audio: Unavailable (Visual mode)")
            self.status_label.setStyleSheet("color: orange;")