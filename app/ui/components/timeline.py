from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QFontMetrics, QColor, QLinearGradient
from typing import Optional, List
import math


class TimelineWidget(QWidget):
    """Visual timeline widget showing guitar strumming patterns with real-time animation."""
    
    step_hit = Signal(int)  # Emitted when a step is hit
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setMinimumWidth(800)
        
        # Pattern data
        self.pattern = None
        self.current_step = 0
        self.steps_per_bar = 8
        self.time_signature = (4, 4)
        
        # Visual properties
        self.step_width = 80
        self.step_height = 120
        self.margin = 40
        self.arrow_size = 30
        
        # Animation properties
        self._highlight_scale = 1.0
        self._flash_opacity = 0.0
        
        # Animation objects
        self.highlight_animation = QPropertyAnimation(self, b"highlight_scale")
        self.highlight_animation.setDuration(150)
        self.highlight_animation.setEasingCurve(QEasingCurve.OutBack)
        
        self.flash_animation = QPropertyAnimation(self, b"flash_opacity")
        self.flash_animation.setDuration(200)
        self.flash_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Colors
        self.bg_color = QColor(240, 240, 245)
        self.step_color = QColor(60, 60, 80)
        self.current_color = QColor(255, 100, 100)
        self.accent_color = QColor(255, 200, 50)
        self.beat_color = QColor(100, 100, 120)
        
        # Font
        self.font = QFont("Arial", 10, QFont.Bold)
        
    def set_pattern(self, pattern):
        """Set the strumming pattern to display."""
        self.pattern = pattern
        if pattern:
            self.steps_per_bar = pattern.steps_per_bar
            self.time_signature = pattern.time_sig
            self.update_geometry()
        self.update()
        
    def set_current_step(self, step: int):
        """Update the current step position with animation."""
        if self.current_step != step:
            self.current_step = step
            self.animate_step_hit()
            self.update()
            
    def animate_step_hit(self):
        """Animate the current step highlight."""
        # Scale animation
        self.highlight_animation.setStartValue(1.0)
        self.highlight_animation.setEndValue(1.3)
        self.highlight_animation.finished.connect(self.reset_highlight_scale)
        self.highlight_animation.start()
        
        # Flash animation
        self.flash_animation.setStartValue(1.0)
        self.flash_animation.setEndValue(0.0)
        self.flash_animation.start()
        
    def reset_highlight_scale(self):
        """Reset highlight scale after animation."""
        self.highlight_scale = 1.0
        self.update()
        
    def get_highlight_scale(self):
        return self._highlight_scale
        
    def set_highlight_scale(self, value):
        self._highlight_scale = value
        self.update()
        
    highlight_scale = property(get_highlight_scale, set_highlight_scale)
    
    def get_flash_opacity(self):
        return self._flash_opacity
        
    def set_flash_opacity(self, value):
        self._flash_opacity = value
        self.update()
        
    flash_opacity = property(get_flash_opacity, set_flash_opacity)
        
    def update_geometry(self):
        """Update widget geometry based on pattern."""
        if not self.pattern:
            return
            
        total_width = self.steps_per_bar * self.step_width + 2 * self.margin
        self.setMinimumWidth(total_width)
        
    def paintEvent(self, event):
        """Draw the timeline visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), self.bg_color)
        
        if not self.pattern:
            painter.setPen(self.step_color)
            painter.setFont(self.font)
            painter.drawText(self.rect(), Qt.AlignCenter, "No pattern selected")
            return
            
        # Calculate positions
        start_x = self.margin
        center_y = self.height() // 2
        
        # Draw beat markers
        self.draw_beat_markers(painter, start_x, center_y - 80)
        
        # Draw steps
        for i in range(self.steps_per_bar):
            step_x = start_x + i * self.step_width
            step = self.pattern.steps[i] if i < len(self.pattern.steps) else None
            
            is_current = (i == self.current_step % self.steps_per_bar)
            self.draw_step(painter, step_x, center_y, step, is_current)
            
        # Draw progress indicator
        self.draw_progress(painter, start_x, center_y + 80)
        
    def draw_beat_markers(self, painter, start_x, y):
        """Draw beat number markers."""
        painter.setPen(QPen(self.beat_color, 2))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        
        beats_per_bar = self.time_signature[0]
        steps_per_beat = self.steps_per_bar // beats_per_bar
        
        for beat in range(beats_per_bar):
            beat_x = start_x + beat * steps_per_beat * self.step_width
            painter.drawText(beat_x - 10, y, 20, 20, Qt.AlignCenter, str(beat + 1))
            
            # Draw beat line
            painter.drawLine(beat_x, y + 15, beat_x, y + 35)
            
    def draw_step(self, painter, x, y, step, is_current):
        """Draw a single step (arrow or rest)."""
        if not step:
            return
            
        # Set colors and scale based on current step
        if is_current:
            scale = self.highlight_scale
            pen_color = self.current_color
            brush_color = QColor(self.current_color)
            brush_color.setAlpha(int(150 + self.flash_opacity * 105))
        else:
            scale = 1.0
            if step.accent > 0.5:
                pen_color = self.accent_color
                brush_color = QColor(self.accent_color)
                brush_color.setAlpha(100)
            else:
                pen_color = self.step_color
                brush_color = QColor(self.step_color)
                brush_color.setAlpha(80)
                
        # Calculate arrow size with scale
        arrow_size = int(self.arrow_size * scale)
        line_width = max(2, int(3 * scale))
        
        # Adjust for accent
        if step.accent > 0.5:
            line_width = int(line_width * 1.5)
            
        painter.setPen(QPen(pen_color, line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QBrush(brush_color))
        
        if step.dir == "D":
            self.draw_down_arrow(painter, x, y, arrow_size)
        elif step.dir == "U":
            self.draw_up_arrow(painter, x, y, arrow_size)
        elif step.dir == "-":
            self.draw_rest(painter, x, y, arrow_size)
            
    def draw_down_arrow(self, painter, x, y, size):
        """Draw downstroke arrow."""
        # Arrow shaft
        shaft_x = x + self.step_width // 2
        painter.drawLine(shaft_x, y - size//2, shaft_x, y + size//2)
        
        # Arrow head
        head_size = size // 3
        painter.drawLine(shaft_x, y + size//2, shaft_x - head_size, y + size//2 - head_size)
        painter.drawLine(shaft_x, y + size//2, shaft_x + head_size, y + size//2 - head_size)
        
    def draw_up_arrow(self, painter, x, y, size):
        """Draw upstroke arrow."""
        # Arrow shaft
        shaft_x = x + self.step_width // 2
        painter.drawLine(shaft_x, y - size//2, shaft_x, y + size//2)
        
        # Arrow head
        head_size = size // 3
        painter.drawLine(shaft_x, y - size//2, shaft_x - head_size, y - size//2 + head_size)
        painter.drawLine(shaft_x, y - size//2, shaft_x + head_size, y - size//2 + head_size)
        
    def draw_rest(self, painter, x, y, size):
        """Draw rest symbol."""
        rest_x = x + self.step_width // 2
        rest_size = size // 4
        
        # Draw rest as small rectangle
        rest_rect = QRect(rest_x - rest_size, y - rest_size//2, rest_size * 2, rest_size)
        painter.drawRect(rest_rect)
        
    def draw_progress(self, painter, start_x, y):
        """Draw progress bar showing position in the bar."""
        if not self.pattern:
            return
            
        bar_width = self.steps_per_bar * self.step_width
        progress_width = (self.current_step % self.steps_per_bar) * self.step_width
        
        # Background
        painter.setPen(QPen(self.step_color, 1))
        painter.setBrush(QBrush(QColor(200, 200, 220)))
        painter.drawRect(start_x, y, bar_width, 10)
        
        # Progress fill
        if progress_width > 0:
            gradient = QLinearGradient(start_x, y, start_x + progress_width, y)
            gradient.setColorAt(0, self.current_color)
            gradient.setColorAt(1, self.accent_color)
            painter.setBrush(QBrush(gradient))
            painter.drawRect(start_x, y, progress_width, 10)
            
        # Current position indicator
        indicator_x = start_x + progress_width
        painter.setPen(QPen(self.current_color, 3))
        painter.drawLine(indicator_x, y - 5, indicator_x, y + 15)