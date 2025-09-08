#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer

# Import the widget and pattern classes
from app.ui.components.steps_preview import StepsPreviewWidget
from app.core.patterns import StrumPattern, Step

def create_test_pattern():
    """Create a simple test pattern."""
    steps = [
        Step(t=0.0, dir="D", technique="open", accent=0.8),
        Step(t=0.125, dir="U", technique="open", accent=0.0),
        Step(t=0.25, dir="D", technique="open", accent=0.3),
        Step(t=0.375, dir="U", technique="open", accent=0.0),
        Step(t=0.5, dir="D", technique="open", accent=0.0),
        Step(t=0.625, dir="U", technique="open", accent=0.0),
        Step(t=0.75, dir="D", technique="open", accent=1.0),
        Step(t=0.875, dir="U", technique="open", accent=0.0),
    ]
    
    return StrumPattern(
        id="test_rock",
        name="Test Rock Pattern",
        time_sig=(4, 4),
        steps_per_bar=8,
        bpm_default=120,
        bpm_min=60,
        bpm_max=180,
        steps=steps,
        notes="Test pattern for preview widget"
    )

def main():
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Steps Preview Test")
    window.resize(400, 300)
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Create preview widget
    preview_widget = StepsPreviewWidget()
    layout.addWidget(preview_widget)
    
    window.setCentralWidget(central_widget)
    
    # Set test pattern
    test_pattern = create_test_pattern()
    preview_widget.set_pattern(test_pattern)
    preview_widget.set_bpm(120)
    
    # Timer to simulate step progression
    step_timer = QTimer()
    current_step = [0]  # Use list to allow modification in closure
    
    def next_step():
        preview_widget.set_current_step(current_step[0])
        current_step[0] = (current_step[0] + 1) % 8
    
    step_timer.timeout.connect(next_step)
    step_timer.start(500)  # Change step every 500ms for testing
    
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())