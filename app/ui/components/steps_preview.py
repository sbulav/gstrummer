from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QPixmap
from typing import Optional

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

        # Visual properties
        self.main_arrow_size = 120  # Large arrow for next action
        self.small_arrow_size = 60  # Small arrow for action+1
        self.vertical_spacing = 100

        # Colors
        self.bg_color = QColor(245, 245, 250)
        self.next_color = QColor(100, 150, 255)  # Blue for next
        self.upcoming_color = QColor(150, 150, 170)  # Gray for upcoming
        self.accent_color = QColor(255, 150, 50)  # Orange for accents
        self.text_color = QColor(50, 50, 70)

    def set_pattern(self, pattern):
        """Set the strumming pattern."""
        self.pattern = pattern
        self.update()

    def set_current_step(self, step: int):
        """Update current step position."""
        if self.current_step != step:
            self.current_step = step
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

        if not self.pattern:
            painter.setPen(self.upcoming_color)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Выберите ритм")
            return

        # Title
        painter.setPen(QPen(self.text_color, 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(10, 25, "Следующий удар:")

        # Draw upcoming steps
        upcoming_steps = self.get_upcoming_steps()

        # Center positions
        center_x = self.width() // 2
        main_y = self.height() // 2 - 20  # Main arrow position
        small_y = main_y + self.vertical_spacing  # Small arrow position below

        # Draw main next step (big arrow)
        if len(upcoming_steps) > 0 and upcoming_steps[0][1]:
            step = upcoming_steps[0][1]
            self.draw_main_step(painter, center_x, main_y, step)

        # Draw action+1 (small arrow below)
        if len(upcoming_steps) > 1 and upcoming_steps[1][1]:
            step = upcoming_steps[1][1]
            self.draw_small_step(painter, center_x, small_y, step)

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

        # Draw "СЛЕДУЮЩИЙ" label above
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QPen(color, 2))
        painter.drawText(x - 40, y - arrow_size // 2 - 15, "СЛЕДУЮЩИЙ")

        # Draw accent indicator if needed
        cue_y = y + arrow_size // 2 + 25
        if step.accent > 0.5:
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.drawText(x - 15, cue_y, "АКЦЕНТ!")
            cue_y += 25

        # Draw technique cue (icon or text) below the arrow
        self.draw_technique_cue(painter, x, cue_y, step.technique, position="below")

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

        # Draw "затем" label above small arrow
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(color, 1))
        painter.drawText(x - 15, y - arrow_size // 2 - 5, "затем")

        # Draw technique cue to the right of the arrow
        self.draw_technique_cue(
            painter, x + arrow_size // 2 + 10, y, step.technique, position="right"
        )

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
        """Draw large downstroke arrow."""
        # Vertical shaft
        shaft_length = size // 2
        painter.drawLine(x, y - shaft_length // 2, x, y + shaft_length // 2)

        # Arrow head - bigger and more prominent
        head_size = size // 3
        painter.drawLine(
            x, y + shaft_length // 2, x - head_size, y + shaft_length // 2 - head_size
        )
        painter.drawLine(
            x, y + shaft_length // 2, x + head_size, y + shaft_length // 2 - head_size
        )

    def draw_large_up_arrow(self, painter, x, y, size):
        """Draw large upstroke arrow."""
        # Vertical shaft
        shaft_length = size // 2
        painter.drawLine(x, y - shaft_length // 2, x, y + shaft_length // 2)

        # Arrow head - bigger and more prominent
        head_size = size // 3
        painter.drawLine(
            x, y - shaft_length // 2, x - head_size, y - shaft_length // 2 + head_size
        )
        painter.drawLine(
            x, y - shaft_length // 2, x + head_size, y - shaft_length // 2 + head_size
        )

    def draw_large_rest(self, painter, x, y, size):
        """Draw large rest symbol."""
        rest_size = size // 3
        # Draw as thick horizontal line
        painter.drawLine(x - rest_size, y, x + rest_size, y)

        # Add small vertical lines at ends for better visibility
        painter.drawLine(x - rest_size, y - 5, x - rest_size, y + 5)
        painter.drawLine(x + rest_size, y - 5, x + rest_size, y + 5)
