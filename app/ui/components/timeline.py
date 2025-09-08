from time import monotonic

from PySide6.QtCore import QPoint, QRect, Qt, Signal, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QPolygon,
)
from PySide6.QtWidgets import QWidget


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
        self.show_grid = True

        # Animation properties
        self._highlight_scale = 1.0

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self.reset_highlight_scale)

        # Timing
        self.bpm = 120
        self.last_step_time = None
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update)
        self.countdown_timer.start(50)

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

    def set_bpm(self, bpm: int) -> None:
        """Set current tempo for countdown calculations."""
        self.bpm = bpm
        self.update()

    def set_current_step(self, step: int):
        """Update the current step position with animation."""
        if self.current_step != step:
            self.current_step = step
            self.last_step_time = monotonic()
            self.animate_step_hit()
            self.update()

    def animate_step_hit(self):
        """Animate the current step highlight."""
        # Scale animation
        self.highlight_scale = 1.15
        self.update()
        self.animation_timer.start(150)

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

    def update_geometry(self):
        """Update widget geometry based on pattern."""
        if not self.pattern:
            return

        base_step = 80
        total_width = self.steps_per_bar * base_step + 2 * self.margin
        self.setMinimumWidth(total_width)

    def paintEvent(self, event):
        """Draw the timeline visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Compute dynamic metrics
        bar_width = self.width() - 2 * self.margin
        self.step_width = bar_width / self.steps_per_bar
        bar_height = self.height() - 2 * self.margin
        self.step_height = bar_height
        start_x = self.margin
        start_y = self.margin
        center_y = start_y + bar_height / 2

        # Draw fretboard background
        bar_rect = QRect(int(start_x), int(start_y), int(bar_width), int(bar_height))
        self.draw_fretboard(painter, bar_rect)

        if not self.pattern:
            painter.setPen(self.step_color)
            painter.setFont(self.font)
            painter.drawText(bar_rect, Qt.AlignCenter, "No pattern selected")
            return

        # Optional grid
        if self.show_grid:
            self.draw_grid(painter, start_x, start_y, bar_width, bar_height)

        # Draw beat markers above the fretboard
        self.draw_beat_markers(painter, start_x, int(start_y - 25))

        # Draw steps
        for i in range(self.steps_per_bar):
            step_x = start_x + i * self.step_width
            step = self.pattern.steps[i] if i < len(self.pattern.steps) else None
            is_current = i == self.current_step % self.steps_per_bar
            self.draw_step(painter, step_x, center_y, step, is_current)

        # Draw progress indicator below the fretboard with countdown
        beats_per_bar = self.time_signature[0]
        steps_per_beat = self.steps_per_bar / beats_per_bar
        step_ms = 60000 / self.bpm / steps_per_beat if self.bpm else 0
        if self.last_step_time is None:
            ms_until_next = step_ms
        else:
            elapsed = (monotonic() - self.last_step_time) * 1000
            ms_until_next = max(0, step_ms - elapsed)

        self.draw_progress(
            painter, start_x, int(start_y + bar_height + 10), ms_until_next
        )

    def draw_beat_markers(self, painter, start_x, y):
        """Draw beat numbers with subdivision labels."""
        beats_per_bar = self.time_signature[0]
        steps_per_beat = self.steps_per_bar // beats_per_bar

        beat_font = QFont("Arial", 12, QFont.Bold)
        sub_font = QFont("Arial", 10)
        painter.setPen(QPen(self.beat_color, 2))

        # Template for common subdivision syllables
        subdivision_templates = {
            1: ["1"],
            2: ["1", "&"],
            3: ["1", "&", "a"],
            4: ["1", "e", "&", "a"],
        }
        template = subdivision_templates.get(
            steps_per_beat, [str(i + 1) for i in range(steps_per_beat)]
        )

        for step in range(self.steps_per_bar):
            beat = step // steps_per_beat
            sub = step % steps_per_beat
            label = template[sub]
            if sub == 0:
                label = str(beat + 1)
                painter.setFont(beat_font)
            else:
                painter.setFont(sub_font)

            text_x = int(start_x + (step + 0.5) * self.step_width)
            painter.drawText(text_x - 10, int(y), 20, 20, Qt.AlignCenter, label)

            if sub == 0:
                line_x = int(start_x + step * self.step_width)
                painter.drawLine(line_x, int(y + 15), line_x, int(y + 35))

    def draw_step(self, painter, x, y, step, is_current):
        """Draw a single step (arrow or rest)."""
        if not step:
            return

        # Set colors and scale based on current step
        if is_current:
            scale = self.highlight_scale
            pen_color = QColor(self.current_color)
        else:
            scale = 1.0
            pen_color = self.accent_color if step.accent > 0.5 else self.step_color

        # Calculate arrow size with scale but keep it compact within the grid
        arrow_size = int(self.step_height * 0.6 * scale)
        line_width = max(4, int(4 * scale))

        # Adjust for accent
        if step.accent > 0.5:
            line_width = int(line_width * 1.5)

        painter.setPen(
            QPen(pen_color, line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        )
        painter.setBrush(Qt.NoBrush)

        if step.dir == "D":
            self.draw_down_arrow(painter, x, y, arrow_size)
        elif step.dir == "U":
            self.draw_up_arrow(painter, x, y, arrow_size)
        elif step.dir == "-":
            self.draw_rest(painter, x, y, arrow_size)

    def draw_down_arrow(self, painter, x, y, size):
        """Draw downstroke arrow as a simple filled head with a slim shaft."""
        shaft_x = int(x + self.step_width / 2)
        top = int(y - size / 2)
        bottom = int(y + size / 2)
        painter.drawLine(shaft_x, top, shaft_x, bottom)

        head_width = int(size * 0.5)
        head_height = int(size * 0.35)
        points = [
            QPoint(shaft_x, bottom),
            QPoint(shaft_x - head_width // 2, bottom - head_height),
            QPoint(shaft_x + head_width // 2, bottom - head_height),
        ]
        painter.save()
        painter.setBrush(painter.pen().color())
        painter.drawPolygon(QPolygon(points))
        painter.restore()

    def draw_up_arrow(self, painter, x, y, size):
        """Draw upstroke arrow as a simple filled head with a slim shaft."""
        shaft_x = int(x + self.step_width / 2)
        top = int(y - size / 2)
        bottom = int(y + size / 2)
        painter.drawLine(shaft_x, top, shaft_x, bottom)

        head_width = int(size * 0.5)
        head_height = int(size * 0.35)
        points = [
            QPoint(shaft_x, top),
            QPoint(shaft_x - head_width // 2, top + head_height),
            QPoint(shaft_x + head_width // 2, top + head_height),
        ]
        painter.save()
        painter.setBrush(painter.pen().color())
        painter.drawPolygon(QPolygon(points))
        painter.restore()

    def draw_rest(self, painter, x, y, size):
        """Draw rest symbol."""
        rest_x = int(x + self.step_width / 2)
        rest_size = int(size / 4)

        painter.save()
        color = QColor(self.step_color)
        color.setAlpha(120)
        painter.setBrush(QBrush(color))
        rest_rect = QRect(
            rest_x - rest_size, int(y - rest_size / 2), rest_size * 2, rest_size
        )
        painter.drawRoundedRect(rest_rect, 2, 2)
        painter.restore()

    def draw_progress(self, painter, start_x, y, ms_until_next):
        """Draw progress bar showing position in the bar with countdown."""
        if not self.pattern:
            return

        bar_width = self.steps_per_bar * self.step_width
        progress_width = (self.current_step % self.steps_per_bar) * self.step_width

        # Background
        painter.setPen(QPen(self.step_color, 1))
        painter.setBrush(QBrush(QColor(200, 200, 220)))
        painter.drawRect(int(start_x), int(y), int(bar_width), 10)

        # Progress fill
        if progress_width > 0:
            gradient = QLinearGradient(start_x, y, start_x + progress_width, y)
            gradient.setColorAt(0, self.current_color)
            gradient.setColorAt(1, self.accent_color)
            painter.setBrush(QBrush(gradient))
            painter.drawRect(int(start_x), int(y), int(progress_width), 10)

        # Current position indicator
        indicator_x = int(start_x + progress_width)
        painter.setPen(QPen(self.current_color, 3))
        painter.drawLine(indicator_x, int(y - 5), indicator_x, int(y + 15))

        # Countdown text
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(self.current_color))
        painter.drawText(
            indicator_x + 5,
            int(y + 25),
            f"{int(ms_until_next)} ms",
        )

    def set_show_grid(self, show: bool) -> None:
        """Toggle visibility of the grid overlay."""
        self.show_grid = show
        self.update()

    def draw_fretboard(self, painter: QPainter, rect: QRect) -> None:
        """Draw a simple 6-string guitar fretboard background."""
        painter.save()

        # Wood-like background
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, QColor(200, 170, 120))
        gradient.setColorAt(1, QColor(160, 130, 90))
        painter.fillRect(rect, QBrush(gradient))

        # Border
        painter.setPen(QPen(self.beat_color.darker(150), 2))
        painter.drawRect(rect)

        # Strings
        string_pen = QPen(QColor(230, 230, 230), 2, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(string_pen)
        num_strings = 6
        spacing = rect.height() / (num_strings - 1)
        for i in range(num_strings):
            y = rect.top() + i * spacing
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))

        painter.restore()

    def draw_grid(
        self,
        painter: QPainter,
        start_x: float,
        start_y: float,
        width: float,
        height: float,
    ) -> None:
        """Draw vertical grid lines aligned with the background."""
        pen = QPen(self.beat_color.lighter(180), 1, Qt.DotLine)
        painter.setPen(pen)
        top = int(start_y)
        bottom = int(start_y + height)

        for i in range(self.steps_per_bar + 1):
            x = int(start_x + i * self.step_width)
            painter.drawLine(x, top, x, bottom)
