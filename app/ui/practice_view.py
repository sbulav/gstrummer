from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QSplitter,
    QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QPainter, QPen, QBrush, QColor
from time import monotonic

from .components.timeline import TimelineWidget
from .components.transport import TransportControls
from .components.steps_preview import StepsPreviewWidget
from app.core.evaluator import Evaluator


class PracticeView(QWidget):
    """Enhanced practice view with visual timeline and transport controls."""

    back_requested = Signal()

    def __init__(self, audio_engine, metronome):
        super().__init__()
        self.audio = audio_engine
        self.metronome = metronome
        self.current_pattern = None
        self.patterns = {}
        self.songs = []  # Will be populated with songs data
        self.current_progression = []
        self.current_chord_index = 0

        self.evaluator = Evaluator()

        self.init_ui()
        self.setup_connections()
        self.setup_shortcuts()

    def init_ui(self):
        """Initialize the practice view UI."""
        layout = QVBoxLayout(self)

        # Header with back button and pattern info
        header_layout = QHBoxLayout()

        self.back_button = QPushButton("← Назад в меню")
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)

        header_layout.addStretch()

        self.pattern_title = QLabel("Выберите ритм")
        self.pattern_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.pattern_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.pattern_title)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Timeline visualization (main focus) - now with horizontal split
        timeline_group = QGroupBox("Визуализация ритма")
        timeline_layout = QVBoxLayout(timeline_group)

        # Grid visibility toggle
        controls_line = QHBoxLayout()
        controls_line.addStretch()
        self.grid_checkbox = QCheckBox("Сетка")
        self.grid_checkbox.setChecked(False)
        controls_line.addWidget(self.grid_checkbox)
        timeline_layout.addLayout(controls_line)

        # Horizontal splitter for timeline and preview
        # Horizontal splitter for timeline and preview
        self.timeline_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Timeline widget (left side)
        self.timeline = TimelineWidget()
        self.timeline_splitter.addWidget(self.timeline)
        self.timeline.set_show_grid(self.grid_checkbox.isChecked())

        # Steps preview (right side)
        self.steps_preview = StepsPreviewWidget()
        self.timeline_splitter.addWidget(self.steps_preview)

        # Set proportions: timeline gets 70%, preview gets 30%
        self.timeline_splitter.setStretchFactor(0, 7)
        self.timeline_splitter.setStretchFactor(1, 3)

        timeline_layout.addWidget(self.timeline_splitter)

        splitter.addWidget(timeline_group)

        # Transport controls and pattern info
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        # Transport controls
        self.transport = TransportControls()
        controls_layout.addWidget(self.transport)

        # Chord progression display - Split into two widgets
        progression_group = QGroupBox("Прогрессия аккордов")
        progression_main_layout = QHBoxLayout(progression_group)

        # Left widget - Song name + Next progression button (grouped horizontally)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(5, 10, 5, 10)

        # Song title (to the LEFT of the button)
        self.song_title_label = QLabel("Песня не выбрана")
        self.song_title_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self.song_title_label.setStyleSheet(
            "font-size: 11px; font-weight: 600; margin-right: 8px;"
        )

        # Next progression button
        self.next_progression_button = QPushButton("Следующая\nпрогрессия")
        self.next_progression_button.setMaximumWidth(90)
        self.next_progression_button.setMinimumHeight(60)
        self.next_progression_button.setStyleSheet(
            """
            QPushButton { font-size: 10px; padding: 5px;
                        background-color: #e0e0e0; border: 1px solid #cccccc; border-radius: 5px; }
            QPushButton:hover { background-color: #d0d0d0; }
        """
        )

        button_layout.addWidget(self.song_title_label, 1)
        button_layout.addWidget(
            self.next_progression_button, 0, Qt.AlignmentFlag.AlignRight
        )

        # Right widget - Chord display container
        chord_container = QWidget()
        chord_layout = QVBoxLayout(chord_container)
        chord_layout.setContentsMargins(10, 5, 10, 5)

        # # Song info label
        # self.song_info_label = QLabel("Выберите ритм для отображения прогрессии")
        # self.song_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.song_info_label.setStyleSheet("font-size: 11px; color: gray; margin-bottom: 5px;")
        # chord_layout.addWidget(self.song_info_label)

        # NOTE: No text above the chord container per requirement

        # Custom widget for chord progression display
        self.chord_display_widget = QWidget()
        self.chord_display_widget.setMinimumHeight(90)
        chord_layout.addWidget(self.chord_display_widget, 0, Qt.AlignmentFlag.AlignTop)
        chord_layout.addStretch(1)  # Push content up, leave flexible space below

        # Add both containers to main layout
        progression_main_layout.addWidget(button_container)
        progression_main_layout.addWidget(chord_container)

        # Set stretch factors: 1 for button, 3 for chords (25%/75% split)
        progression_main_layout.setStretchFactor(button_container, 1)
        progression_main_layout.setStretchFactor(chord_container, 3)

        controls_layout.addWidget(progression_group)

        splitter.addWidget(controls_widget)

        # Set splitter proportions (timeline gets most space)
        splitter.setStretchFactor(0, 3)  # Timeline gets 3/4 of space
        splitter.setStretchFactor(1, 1)  # Controls get 1/4 of space

        layout.addWidget(splitter)

        # Override paint event for chord display widget
        self.chord_display_widget.paintEvent = self.chord_display_paint_event

    def chord_display_paint_event(self, event):
        """Custom paint event for chord progression display."""
        painter = QPainter(self.chord_display_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint_chord_progression(painter)

    def setup_connections(self):
        """Setup signal connections between components."""
        # Transport control connections
        self.transport.play_clicked.connect(self.start_practice)
        self.transport.pause_clicked.connect(self.pause_practice)
        self.transport.stop_clicked.connect(self.stop_practice)
        self.transport.bpm_changed.connect(self.on_bpm_changed)
        self.transport.pattern_changed.connect(self.on_pattern_changed)

        # Audio control connections (now through audio status bar)
        self.transport.volume_changed.connect(self.on_volume_changed)
        self.transport.enabled_changed.connect(self.on_enabled_changed)

        # Chord progression connections
        self.next_progression_button.clicked.connect(self.update_chord_progression)

        # Metronome connections
        self.metronome.tick.connect(self.on_metronome_tick)
        self.metronome.started.connect(self.on_metronome_started)
        self.metronome.stopped.connect(self.on_metronome_stopped)

        # Timeline connections
        self.timeline.step_hit.connect(self.on_step_hit)
        self.grid_checkbox.toggled.connect(self.timeline.set_show_grid)

    def set_pattern(self, pattern):
        """Set the current practice pattern."""
        self.current_pattern = pattern
        if pattern:
            # Update UI components
            self.pattern_title.setText(pattern.name)
            self.timeline.set_pattern(pattern)
            self.timeline.set_bpm(pattern.bpm_default)
            self.steps_preview.set_pattern(pattern)

            # Hide or show steps_preview pane for 16 steps
            idx = self.timeline_splitter.indexOf(self.steps_preview)
            if pattern.steps_per_bar == 16:
                if idx != -1:
                    self.timeline_splitter.widget(idx).setParent(None)
                self.timeline_splitter.setStretchFactor(0, 1)
            else:
                if idx == -1:
                    self.timeline_splitter.addWidget(self.steps_preview)
                    self.timeline_splitter.setStretchFactor(0, 7)
                    self.timeline_splitter.setStretchFactor(1, 3)
                self.steps_preview.show()

            # Update transport controls
            self.transport.set_bpm_range(pattern.bpm_min, pattern.bpm_max)
            self.transport.set_bpm(pattern.bpm_default)

            # Update chord progression
            self.update_chord_progression()

            # Configure metronome for this pattern
            beats_per_bar = pattern.time_sig[0]
            self.metronome.steps_per_beat = pattern.steps_per_bar // beats_per_bar
            self.metronome.set_bpm(pattern.bpm_default)

    def set_patterns(self, patterns):
        """Set available patterns for selection."""
        self.patterns = patterns
        self.transport.set_patterns(patterns)

        # Load songs for chord progression suggestions
        try:
            from app.core.patterns import load_songs

            self.songs = load_songs("app/data/songs.yaml")
        except Exception as e:
            print(f"Error loading songs for chord progressions: {e}")
            self.songs = []

    def update_chord_progression(self):
        """Update chord progression display based on current pattern."""
        if not self.current_pattern:
            self.song_title_label.setText("Выберите ритм для отображения прогрессии")
            self.current_progression = []
            self.current_chord_index = 0
            self.chord_display_widget.update()
            return

        matching_songs = [
            song for song in self.songs if song.pattern_id == self.current_pattern.id
        ]

        if matching_songs:
            import random

            selected_song = random.choice(matching_songs)

            self.current_progression = selected_song.progression
            self.current_chord_index = 0
            self.song_title_label.setText(
                f"{selected_song.title} - {selected_song.artist}"
            )

            # NEW: auto-apply BPM for the selected song
            self._apply_song_bpm(selected_song)

        else:
            self.current_progression = []
            self.song_title_label.setText("Нет песен для этого ритма")

        self.chord_display_widget.update()

    def advance_chord(self):
        """Advance to next chord in progression."""
        if self.current_progression:
            self.current_chord_index = (self.current_chord_index + 1) % len(
                self.current_progression
            )
            self.chord_display_widget.update()

    def paint_chord_progression(self, painter):
        """Paint chord progression on the display widget."""
        if not self.current_progression:
            return

        # Visual properties
        chord_width = 80
        chord_height = 60
        chord_spacing = 10
        highlight_color = QColor(100, 200, 100, 200)  # Green highlight
        normal_color = QColor(200, 200, 200, 150)  # Gray normal
        text_color = QColor(50, 50, 50)
        border_color = QColor(100, 100, 100)

        # Calculate positions
        total_width = (
            len(self.current_progression) * (chord_width + chord_spacing)
            - chord_spacing
        )
        start_x = (self.chord_display_widget.width() - total_width) // 2
        y = 10

        # Draw chord boxes
        for i, chord in enumerate(self.current_progression):
            x = start_x + i * (chord_width + chord_spacing)

            # Choose color based on current position
            if i == self.current_chord_index:
                painter.setBrush(QBrush(highlight_color))
            else:
                painter.setBrush(QBrush(normal_color))

            # Draw chord box
            painter.setPen(QPen(border_color, 2))
            painter.drawRoundedRect(x, y, chord_width, chord_height, 8, 8)

            # Draw chord name
            painter.setPen(QPen(text_color))
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.drawText(
                x, y, chord_width, chord_height, Qt.AlignmentFlag.AlignCenter, chord
            )

        # Draw progression indicator (1, 2, 3, 4...)
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(text_color))
        for i in range(len(self.current_progression)):
            x = start_x + i * (chord_width + chord_spacing) + chord_width // 2
            painter.drawText(
                x - 10,
                y + chord_height + 15,
                20,
                15,
                Qt.AlignmentFlag.AlignCenter,
                str(i + 1),
            )

    def start_practice(self):
        """Start practice session."""
        if not self.current_pattern:
            return

        # Configure metronome callback for audio/visual feedback
        self.metronome.set_callback(self.on_practice_tick)
        self.metronome.start()
        self.evaluator.reset()
        self.timeline.clear_accuracy()

    def pause_practice(self):
        """Pause practice session."""
        self.metronome.pause()

    def stop_practice(self):
        """Stop practice session."""
        self.metronome.stop()
        self.timeline.set_current_step(0)
        self.steps_preview.set_current_step(0)

    def on_bpm_changed(self, bpm: int):
        """Handle BPM change from transport controls."""
        self.metronome.set_bpm(bpm)
        self.timeline.set_bpm(bpm)

    def on_pattern_changed(self, pattern_id: str):
        """Handle pattern change from transport controls."""
        if pattern_id and pattern_id in self.patterns:
            # Get the new pattern
            new_pattern = self.patterns[pattern_id]

            # Update current pattern
            self.current_pattern = new_pattern

            # Update UI components with new pattern
            self.pattern_title.setText(new_pattern.name)
            self.timeline.set_pattern(new_pattern)
            self.timeline.set_bpm(new_pattern.bpm_default)
            self.steps_preview.set_pattern(new_pattern)

            # Update chord progression display
            self.update_chord_progression()

            # Hide steps preview for 16-step patterns to avoid overlap
            if new_pattern.steps_per_bar == 16:
                # Remove steps_preview if still present
                idx = self.timeline_splitter.indexOf(self.steps_preview)
                if idx != -1:
                    self.timeline_splitter.widget(idx).setParent(None)
                self.timeline_splitter.setStretchFactor(0, 1)  # timeline gets 100%
            else:
                # Add steps_preview back if missing
                idx = self.timeline_splitter.indexOf(self.steps_preview)
                if idx == -1:
                    self.timeline_splitter.addWidget(self.steps_preview)
                    self.timeline_splitter.setStretchFactor(0, 7)
                    self.timeline_splitter.setStretchFactor(1, 3)
                self.steps_preview.show()

            # Configure metronome for the new pattern
            beats_per_bar = new_pattern.time_sig[0]
            self.metronome.steps_per_beat = new_pattern.steps_per_bar // beats_per_bar
            self.metronome.set_bpm(new_pattern.bpm_default)

            # Reset timeline position when pattern changes
            self.timeline.set_current_step(0)
            self.steps_preview.set_current_step(0)

    def on_volume_changed(self, volume_type: str, value: float):
        """Handle volume changes from transport controls."""
        if volume_type == "master":
            self.audio.set_volumes(master=value)
        elif volume_type == "click":
            self.audio.set_volumes(click=value)
        elif volume_type == "strum":
            self.audio.set_volumes(strum=value)

    def on_enabled_changed(self, audio_type: str, enabled: bool):
        """Handle enable/disable changes for audio types."""
        if audio_type == "click":
            self.audio.set_click_enabled(enabled)
        elif audio_type == "strum":
            self.audio.set_strum_enabled(enabled)

    def on_metronome_tick(self, timestamp: float, step_index: int):
        """Handle metronome tick for GUI updates (Qt signal, thread-safe)."""
        if not self.current_pattern:
            return

        # Update timeline visualization
        self.timeline.set_current_step(step_index)
        self.steps_preview.set_current_step(step_index)

        result = self.evaluator.add_step(step_index, timestamp)
        if result:
            self.timeline.set_step_accuracy(result.step_index, result.deviation_ms)

        # Advance chord progression on bar boundaries
        if step_index % self.current_pattern.steps_per_bar == 0:
            self.advance_chord()

    def on_practice_tick(self, timestamp: float, step_index: int):
        """Handle metronome tick for audio feedback (callback)."""
        if not self.current_pattern:
            return

        bar_length = self.current_pattern.steps_per_bar
        bar_step = step_index % bar_length

        # Play audio feedback
        if bar_step < len(self.current_pattern.steps):
            step = self.current_pattern.steps[bar_step]

            # Play strum sound
            if step.dir != "-":
                current_chord = (
                    self.current_progression[self.current_chord_index]
                    if self.current_progression
                    else None
                )
                self.audio.play_strum(
                    step.dir, step.accent, step.technique, chord=current_chord
                )

            # Compute timing for next step
            next_step = self.current_pattern.steps[
                (bar_step + 1) % len(self.current_pattern.steps)
            ]
            delta_t = (next_step.t - step.t) % 1.0
            beats_per_bar = self.current_pattern.time_sig[0]
            bar_duration = 60.0 / self.metronome.bpm * beats_per_bar
            self.metronome.set_step_duration(delta_t * bar_duration)

            # Play metronome click with beat awareness
            beats_per_bar = self.current_pattern.time_sig[0]
            steps_per_beat = bar_length // beats_per_bar

            if bar_step == 0:
                # Strong beat (downbeat) - use high click
                self.audio.play_click_high()
            elif bar_step % steps_per_beat == 0:
                # Other beats - use accented click
                self.audio.play_click(accent=True)
            # No click on off-beats for cleaner sound

    def on_metronome_started(self):
        """Handle metronome start."""
        self.transport.set_playing(True)

    def on_metronome_stopped(self):
        """Handle metronome stop."""
        self.transport.set_playing(False)

    def on_step_hit(self, step_index: int):
        """Register manual onset from timeline widget."""
        self.evaluator.add_onset(monotonic())

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for better UX."""
        # Play/Pause - Space bar
        self.play_shortcut = QShortcut(QKeySequence("Space"), self)
        self.play_shortcut.activated.connect(self.transport.on_play_pause_clicked)

        # Stop - Escape
        self.stop_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.stop_shortcut.activated.connect(self.transport.on_stop_clicked)

        # BPM adjustment
        self.bpm_up_shortcut = QShortcut(QKeySequence("+"), self)
        self.bpm_up_shortcut.activated.connect(lambda: self.transport.adjust_bpm(5))

        self.bpm_down_shortcut = QShortcut(QKeySequence("-"), self)
        self.bpm_down_shortcut.activated.connect(lambda: self.transport.adjust_bpm(-5))

        # Back to menu - Alt+Left
        self.back_shortcut = QShortcut(QKeySequence("Alt+Left"), self)
        self.back_shortcut.activated.connect(self.back_requested.emit)

    def cleanup(self):
        """Cleanup when view is closed."""
        self.metronome.stop()

    def _apply_song_bpm(self, song):
        """Try to read a BPM from the song and apply it safely."""
        bpm = None
        for attr in ("bpm", "tempo", "target_bpm", "default_bpm"):
            v = getattr(song, attr, None)
            if isinstance(v, (int, float)):
                bpm = int(v)
                break

        if bpm is None:
            return  # no tempo info on song; keep current BPM

        # Clamp to the current pattern range if present
        if self.current_pattern:
            bpm = max(
                self.current_pattern.bpm_min, min(self.current_pattern.bpm_max, bpm)
            )

        # Apply BPM to UI + audio
        self.transport.set_bpm(bpm)
        self.metronome.set_bpm(bpm)
        self.timeline.set_bpm(bpm)
