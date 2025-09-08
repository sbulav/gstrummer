from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QPixmap, QPolygon
from typing import Optional
from time import monotonic

from app.ui.icons import get_technique_icon


class StepsPreviewWidget(QWidget):
    """Widget showing upcoming strumming steps with large arrows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)

        # Pattern data
        self.pattern = None
        self.current_step = 0
        self.preview_count = 2  # Show next 2 steps (current + next)
        
        # Timing for fill animation
        self.bpm = 120
        self.last_step_time = None
        self.fill_progress = 0.0  # 0.0 to 1.0, progress until next beat
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_fill_progress)
        self.animation_timer.start(50)  # Update every 50ms

        # Visual properties
        self.main_arrow_size = 100  # Large arrow for next action (reduced for better centering)
        self.small_arrow_size = 50  # Small arrow for action+1 (reduced for top corner)
        self.vertical_spacing = 100

        # Colors
        self.bg_color = QColor(245, 245, 250)
        self.next_color = QColor(100, 150, 255)  # Blue for next
        self.upcoming_color = QColor(150, 150, 170)  # Gray for upcoming
        self.accent_color = QColor(255, 150, 50)  # Orange for accents
        self.text_color = QColor(50, 50, 70)
        self.fill_color = QColor(150, 255, 150, 80)  # Light green with transparency

    def set_pattern(self, pattern):
        """Set the strumming pattern."""
        self.pattern = pattern
        self.update()

    def set_current_step(self, step: int):
        """Update current step position."""
        if self.current_step != step:
            self.current_step = step
            self.last_step_time = monotonic()
            self.update()
    
    def set_bpm(self, bpm: int):
        """Set current BPM for timing calculations."""
        self.bpm = bpm
        
    def update_fill_progress(self):
        """Update fill progress based on elapsed time since last step."""
        if not self.pattern or not self.last_step_time:
            self.fill_progress = 0.0
            return
            
        # Calculate time per step
        beats_per_bar = 4  # Assume 4/4 for now
        steps_per_beat = self.pattern.steps_per_bar / beats_per_bar
        step_duration = 60.0 / self.bpm / steps_per_beat if self.bpm else 0
        
        elapsed = monotonic() - self.last_step_time
        if step_duration > 0:
            self.fill_progress = min(1.0, elapsed / step_duration)
        else:
            self.fill_progress = 0.0
        
        self.update()

    def get_upcoming_steps(self):
        """Get list of upcoming steps to display."""
        if not self.pattern:
            return []

        upcoming = []
        bar_length = self.pattern.steps_per_bar

        for i in range(self.preview_count):
            step_idx = (self.current_step + i) % bar_length
            if step_idx < len(self.pattern.steps):
                upcoming.append((i, self.pattern.steps[step_idx]))
            else:
                upcoming.append((i, None))

        return upcoming

    def paintEvent(self, event):
        """Draw the preview pane."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Draw animated fill (light green progress)
        if self.pattern and self.fill_progress > 0:
            fill_height = int(self.height() * self.fill_progress)
            fill_rect = painter.window()
            fill_rect.setTop(self.height() - fill_height)
            painter.fillRect(fill_rect, self.fill_color)

        if not self.pattern:
            painter.setPen(self.upcoming_color)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Выберите ритм")
            return

        # Title in top left
        painter.setPen(QPen(self.text_color, 2))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(10, 20, "Удар:")

        # Draw upcoming steps
        upcoming_steps = self.get_upcoming_steps()

        # Center positions
        center_x = self.width() // 2
        main_y = self.height() // 2  # Main arrow position (centered)
        
        # Small arrow position - right top corner
        small_x = self.width() - 60  # 60px from right edge
        small_y = 60  # 60px from top

        # Draw main next step (big arrow)
        if len(upcoming_steps) > 0 and upcoming_steps[0][1]:
            step = upcoming_steps[0][1]
            self.draw_main_step(painter, center_x, main_y, step)

        # Draw action+1 (small arrow in top right)
        if len(upcoming_steps) > 1 and upcoming_steps[1][1]:
            step = upcoming_steps[1][1]
            self.draw_small_step(painter, small_x, small_y, step)

    def draw_main_step(self, painter, x, y, step):
        """Draw the main (next) step with large arrow in center."""
        # Colors and sizes based on accent
        if step.accent > 0.5:
            color = self.accent_color
            arrow_size = int(self.main_arrow_size * 1.2)
            line_width = 8
        else:
            color = self.next_color
            arrow_size = self.main_arrow_size
            line_width = 6

        painter.setPen(
            QPen(
                color,
                line_width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 120)))

        # Draw main arrow
        if step.dir == "D":
            self.draw_large_down_arrow(painter, x, y, arrow_size)
        elif step.dir == "U":
            self.draw_large_up_arrow(painter, x, y, arrow_size)
        elif step.dir == "-":
            self.draw_large_rest(painter, x, y, arrow_size)





    def draw_small_step(self, painter, x, y, step):
        """Draw the action+1 step with smaller arrow below."""
        color = self.upcoming_color
        arrow_size = self.small_arrow_size
        line_width = 3

        painter.setPen(
            QPen(
                color,
                line_width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 80)))

        # Draw small arrow
        if step.dir == "D":
            self.draw_large_down_arrow(painter, x, y, arrow_size)
        elif step.dir == "U":
            self.draw_large_up_arrow(painter, x, y, arrow_size)
        elif step.dir == "-":
            self.draw_large_rest(painter, x, y, arrow_size)

        # Draw "затем" label above small arrow in top right corner
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(color, 1))
        painter.drawText(x - 15, y - arrow_size // 2 - 15, "затем")



    def draw_technique_cue(
        self, painter, x, y, technique: str, position: str = "below"
    ):
        """Draw technique icon or fallback text at given position."""
        pixmap: Optional[QPixmap] = get_technique_icon(technique)
        if pixmap:
            if position == "below":
                painter.drawPixmap(x - pixmap.width() // 2, y, pixmap)
            elif position == "right":
                painter.drawPixmap(x, y - pixmap.height() // 2, pixmap)
            else:
                painter.drawPixmap(x, y, pixmap)
        else:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QPen(self.text_color, 1))
            if position == "below":
                painter.drawText(x - 20, y + 15, technique)
            elif position == "right":
                painter.drawText(x, y + 5, technique)
            else:
                painter.drawText(x, y, technique)

    def draw_large_down_arrow(self, painter, x, y, size):
        """Draw large downstroke arrow with filled head."""
        # Vertical shaft
        shaft_length = size // 2
        painter.drawLine(x, y - shaft_length // 2, x, y + shaft_length // 2)

        # Arrow head - filled triangle like in timeline
        head_width = int(size * 0.5)
        head_height = int(size * 0.35)
        bottom = y + shaft_length // 2
        points = [
            QPoint(x, bottom),
            QPoint(x - head_width // 2, bottom - head_height),
            QPoint(x + head_width // 2, bottom - head_height),
        ]
        painter.save()
        painter.setBrush(QBrush(painter.pen().color()))
        painter.drawPolygon(QPolygon(points))
        painter.restore()

    def draw_large_up_arrow(self, painter, x, y, size):
        """Draw large upstroke arrow with filled head."""
        # Vertical shaft
        shaft_length = size // 2
        painter.drawLine(x, y - shaft_length // 2, x, y + shaft_length // 2)

        # Arrow head - filled triangle like in timeline
        head_width = int(size * 0.5)
        head_height = int(size * 0.35)
        top = y - shaft_length // 2
        points = [
            QPoint(x, top),
            QPoint(x - head_width // 2, top + head_height),
            QPoint(x + head_width // 2, top + head_height),
        ]
        painter.save()
        painter.setBrush(QBrush(painter.pen().color()))
        painter.drawPolygon(QPolygon(points))
        painter.restore()

    def draw_large_rest(self, painter, x, y, size):
        """Draw large rest symbol as rounded rectangle like in timeline."""
        rest_size = int(size / 4)
        
        painter.save()
        color = QColor(150, 150, 170)  # Gray color for rests
        color.setAlpha(120)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color))
        
        rest_rect = QRect(
            x - rest_size, y - rest_size // 2, rest_size * 2, rest_size
        )
        painter.drawRoundedRect(rest_rect, 2, 2)
        painter.restore()
