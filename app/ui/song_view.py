from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QSplitter,
    QCheckBox,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from .components.timeline import TimelineWidget
from .components.transport import TransportControls
from .components.steps_preview import StepsPreviewWidget
from .components.progression_controls import ProgressionControlsWidget
from .components.chord_display import ChordDisplayWidget
from .components.song_info_popup import SongInfoPopup


class SongView(QWidget):
    """Song view for practicing full songs with verse/chorus structure."""

    back_requested = Signal()

    def __init__(self, audio_engine, metronome):
        super().__init__()
        self.audio = audio_engine
        self.metronome = metronome
        self.current_song = None
        self.current_section = None
        self.patterns = {}
        self.songs = []
        self.current_section_index = 0
        self.song_info_popup = None
        # Currently selected pattern override (None means use song defaults)
        self.override_pattern_id: str | None = None

        self.init_ui()
        self.setup_connections()
        self.setup_shortcuts()

    def init_ui(self):
        """Initialize the song view UI."""
        layout = QVBoxLayout(self)

        # Header with back button and song selector
        header_layout = QHBoxLayout()

        self.back_button = QPushButton("← Назад в меню")
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)

        header_layout.addStretch()

        # Song selector
        header_layout.addWidget(QLabel("Песня:"))
        self.song_combo = QComboBox()
        self.song_combo.setMinimumWidth(300)
        self.song_combo.currentTextChanged.connect(self.on_song_changed)
        header_layout.addWidget(self.song_combo)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Main content area with splitter
        splitter = QSplitter(Qt.Vertical)

        # Song structure and section selection
        structure_group = QGroupBox("Структура песни")
        structure_layout = QVBoxLayout(structure_group)

        # Section selector
        section_layout = QHBoxLayout()
        section_layout.addWidget(QLabel("Текущая секция:"))

        self.section_combo = QComboBox()
        self.section_combo.currentTextChanged.connect(self.on_section_changed)
        section_layout.addWidget(self.section_combo)

        section_layout.addStretch()

        # Auto-advance checkbox
        self.auto_advance = QCheckBox("Авто-переход между секциями")
        self.auto_advance.setChecked(False)
        section_layout.addWidget(self.auto_advance)

        structure_layout.addLayout(section_layout)

        # Chord section with two panes
        chord_section_layout = QHBoxLayout()

        # Left pane: progression controls
        progression_group = QGroupBox("Управление песней")
        progression_group_layout = QVBoxLayout(progression_group)
        self.progression_controls = ProgressionControlsWidget()
        self.progression_controls.next_progression_clicked.connect(self.next_section)
        progression_group_layout.addWidget(self.progression_controls)
        chord_section_layout.addWidget(progression_group)

        # Right pane: chord display
        chords_group = QGroupBox("Аккорды")
        chords_group_layout = QVBoxLayout(chords_group)
        self.chord_display = ChordDisplayWidget()
        chords_group_layout.addWidget(self.chord_display)
        chord_section_layout.addWidget(chords_group)

        # Give more space to the chord display
        chord_section_layout.setStretch(0, 1)
        chord_section_layout.setStretch(1, 3)

        structure_layout.addLayout(chord_section_layout)

        # Current section info
        section_info_layout = QHBoxLayout()
        self.current_section_label = QLabel("Секция: -")
        self.current_section_label.setFont(QFont("Arial", 12, QFont.Bold))
        section_info_layout.addWidget(self.current_section_label)

        section_info_layout.addStretch()

        self.section_progress = QLabel("- / -")
        section_info_layout.addWidget(self.section_progress)

        structure_layout.addLayout(section_info_layout)

        splitter.addWidget(structure_group)

        # Timeline visualization
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
        timeline_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Timeline widget (left side)
        self.timeline = TimelineWidget()
        timeline_splitter.addWidget(self.timeline)
        self.timeline.set_show_grid(self.grid_checkbox.isChecked())

        # Steps preview (right side)
        self.steps_preview = StepsPreviewWidget()
        timeline_splitter.addWidget(self.steps_preview)

        # Set proportions: timeline gets 70%, preview gets 30%
        timeline_splitter.setStretchFactor(0, 7)
        timeline_splitter.setStretchFactor(1, 3)

        timeline_layout.addWidget(timeline_splitter)

        splitter.addWidget(timeline_group)

        # Transport controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        # Transport controls
        self.transport = TransportControls()
        controls_layout.addWidget(self.transport)

        splitter.addWidget(controls_widget)

        # Set splitter proportions (rhythm visualization gets most space like in practice view)
        splitter.setStretchFactor(0, 1)  # Structure
        splitter.setStretchFactor(1, 3)  # Rhythm visualization gets 3x more space
        splitter.setStretchFactor(2, 1)  # Transport controls

        layout.addWidget(splitter)

        # Section navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()

        self.prev_section_btn = QPushButton("◀ Предыдущая секция")
        self.prev_section_btn.clicked.connect(self.previous_section)
        nav_layout.addWidget(self.prev_section_btn)

        # Song info button
        self.song_info_btn = QPushButton("ℹ Информация о песне")
        self.song_info_btn.clicked.connect(self.show_song_info_popup)
        nav_layout.addWidget(self.song_info_btn)

        self.next_section_btn = QPushButton("Следующая секция ▶")
        self.next_section_btn.clicked.connect(self.next_section)
        nav_layout.addWidget(self.next_section_btn)

        nav_layout.addStretch()

        layout.addLayout(nav_layout)

    def setup_connections(self):
        """Setup signal connections between components."""
        # Transport control connections
        self.transport.play_clicked.connect(self.start_practice)
        self.transport.pause_clicked.connect(self.pause_practice)
        self.transport.stop_clicked.connect(self.stop_practice)
        self.transport.bpm_changed.connect(self.on_bpm_changed)
        self.transport.pattern_changed.connect(self.on_pattern_changed)

        # Audio control connections
        self.transport.volume_changed.connect(self.on_volume_changed)
        self.transport.enabled_changed.connect(self.on_enabled_changed)

        # Metronome connections
        self.metronome.tick.connect(self.on_metronome_tick)
        self.metronome.started.connect(self.on_metronome_started)
        self.metronome.stopped.connect(self.on_metronome_stopped)

        # Timeline connections
        self.timeline.step_hit.connect(self.on_step_hit)
        self.grid_checkbox.toggled.connect(self.timeline.set_show_grid)

    def set_song(self, song):
        """Set the current song for practice."""
        self.current_song = song
        # Reset any pattern override when switching songs
        self.override_pattern_id = None
        if song:
            # Update progression controls and chord display
            self.progression_controls.set_song(song)
            self.chord_display.set_song(song)

            # Setup sections
            self.setup_song_structure()

    def setup_song_structure(self):
        """Setup the song structure UI elements."""
        if not self.current_song:
            return

        # Clear section combo
        self.section_combo.clear()

        if self.current_song.has_extended_structure():
            # Add sections from structure
            section_names = self.current_song.get_section_names()
            for section_name in section_names:
                display_name = section_name.replace("_", " ").title()
                self.section_combo.addItem(display_name, section_name)

            # Enable navigation buttons
            self.prev_section_btn.setEnabled(True)
            self.next_section_btn.setEnabled(True)
            self.section_combo.setEnabled(True)

            # Select first section
            if section_names:
                self.current_section_index = 0
                self.section_combo.setCurrentIndex(0)
                self.load_current_section()
        else:
            # Simple song - just add "Practice" mode
            self.section_combo.addItem("Упражнение", "practice")
            self.prev_section_btn.setEnabled(False)
            self.next_section_btn.setEnabled(False)
            self.section_combo.setEnabled(False)
            self.load_practice_mode()

    def load_current_section(self):
        """Load the currently selected section."""
        if not self.current_song or not self.current_song.has_extended_structure():
            return

        section_names = self.current_song.get_section_names()
        if self.current_section_index >= len(section_names):
            return

        section_name = section_names[self.current_section_index]
        section = self.current_song.get_section(section_name)

        if not section:
            return

        self.current_section = section

        # Update section label
        display_name = section_name.replace("_", " ").title()
        self.current_section_label.setText(f"Секция: {display_name}")

        # Update progress
        total_sections = len(section_names)
        self.section_progress.setText(
            f"{self.current_section_index + 1} / {total_sections}"
        )

        # Determine pattern to use (override or section default)
        pattern_id = self.override_pattern_id or section.pattern
        pattern = self.patterns.get(pattern_id)
        bpm = section.bpm_override or self.current_song.bpm
        if pattern:
            # Clamp BPM to pattern range
            bpm = max(pattern.bpm_min, min(pattern.bpm_max, bpm))
            self.load_pattern_for_section(pattern, bpm)
            self.transport.select_pattern(pattern_id)

        # Update chord display for this section
        self.chord_display.set_section(section)

        # Update BPM (section override or song default)
        self.transport.set_bpm(bpm)
        self.metronome.set_bpm(bpm)
        self.timeline.set_bpm(bpm)

    def load_practice_mode(self):
        """Load simple practice mode for songs without structure."""
        if not self.current_song:
            return

        self.current_section_label.setText("Режим: Упражнение")
        self.section_progress.setText("1 / 1")

        # Load main pattern (or overridden)
        pattern_id = self.override_pattern_id or self.current_song.pattern_id
        pattern = self.patterns.get(pattern_id)
        if pattern:
            bpm = max(
                pattern.bpm_min,
                min(pattern.bpm_max, self.current_song.bpm),
            )
            self.load_pattern_for_section(pattern, bpm)
            self.transport.set_bpm(bpm)
            self.metronome.set_bpm(bpm)
            self.timeline.set_bpm(bpm)
            self.transport.select_pattern(pattern_id)

    def load_pattern_for_section(self, pattern, bpm):
        """Load a pattern configured with a specific BPM."""
        self.timeline.set_pattern(pattern)
        self.timeline.set_bpm(bpm)
        self.steps_preview.set_pattern(pattern)

        # Update transport controls
        self.transport.set_bpm_range(pattern.bpm_min, pattern.bpm_max)

        # Configure metronome
        beats_per_bar = pattern.time_sig[0]
        self.metronome.steps_per_beat = pattern.steps_per_bar // beats_per_bar

    def set_patterns(self, patterns):
        """Set available patterns."""
        self.patterns = patterns
        self.transport.set_patterns(patterns)

    def set_songs(self, songs):
        """Set available songs."""
        self.songs = songs
        self.populate_song_combo()

    def populate_song_combo(self):
        """Populate the song selection combo box."""
        self.song_combo.clear()
        self.song_combo.addItem("Выберите песню...", None)

        for song in self.songs:
            display_name = f"{song.artist} - {song.title}"
            self.song_combo.addItem(display_name, song)

    def on_song_changed(self, song_text: str):
        """Handle song selection change."""
        song = self.song_combo.currentData()
        if song:
            self.set_song(song)

    def show_song_info_popup(self):
        """Show the song information popup dialog."""
        if not self.current_song:
            return

        if not self.song_info_popup:
            self.song_info_popup = SongInfoPopup(self)

        self.song_info_popup.set_song(self.current_song)
        self.song_info_popup.exec()

    def on_section_changed(self, section_text):
        """Handle section change from combo box."""
        if not self.current_song:
            return

        section_data = self.section_combo.currentData()
        if section_data == "practice":
            self.load_practice_mode()
        else:
            # Find section index
            section_names = self.current_song.get_section_names()
            if section_data in section_names:
                self.current_section_index = section_names.index(section_data)
                self.load_current_section()

    def previous_section(self):
        """Navigate to previous section."""
        if not self.current_song or not self.current_song.has_extended_structure():
            return
        if self.current_section_index > 0:
            self.current_section_index -= 1
            self.section_combo.setCurrentIndex(self.current_section_index)
            self.load_current_section()

    def next_section(self):
        """Navigate to next section."""
        if not self.current_song or not self.current_song.has_extended_structure():
            return

        section_names = self.current_song.get_section_names()
        if self.current_section_index < len(section_names) - 1:
            self.current_section_index += 1
            self.section_combo.setCurrentIndex(self.current_section_index)
            self.load_current_section()

    def start_practice(self):
        """Start practice session."""
        if not self.current_song:
            return

        # Configure metronome callback for audio/visual feedback
        self.metronome.set_callback(self.on_practice_tick)
        self.metronome.start()

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
        """Handle pattern selection change from transport controls."""
        if pattern_id not in self.patterns:
            return
        self.override_pattern_id = pattern_id
        pattern = self.patterns[pattern_id]
        # Clamp BPM to pattern range while preserving current tempo if possible
        bpm = max(
            pattern.bpm_min,
            min(pattern.bpm_max, self.transport.current_bpm),
        )
        self.load_pattern_for_section(pattern, bpm)
        self.transport.set_bpm(bpm)
        self.metronome.set_bpm(bpm)
        self.timeline.set_bpm(bpm)

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
        """Handle metronome tick for GUI updates."""
        # Update timeline visualization
        self.timeline.set_current_step(step_index)
        self.steps_preview.set_current_step(step_index)

        # Update chord progression highlighting
        self._update_chord_highlighting(step_index)

        # Handle auto-advance between sections
        if self.auto_advance.isChecked() and self.current_section:
            # Calculate if we've completed this section
            pattern = self.patterns.get(
                self.override_pattern_id or self.current_section.pattern
            )
            if pattern:
                steps_per_bar = pattern.steps_per_bar
                completed_bars = step_index // steps_per_bar

                # Check if we've completed the required bars for this section
                if (
                    completed_bars
                    >= self.current_section.bars * self.current_section.repeat
                ):
                    # Auto-advance to next section
                    self.next_section()

    def _update_chord_highlighting(self, step_index: int):
        """Update chord highlighting based on current step."""
        if not self.current_section:
            return

        # Get pattern to calculate bars
        pattern = self.patterns.get(
            self.override_pattern_id or self.current_section.pattern
        )
        if not pattern:
            return

        # Calculate current bar and chord index
        steps_per_bar = pattern.steps_per_bar
        current_bar = (step_index // steps_per_bar) % len(self.current_section.chords)

        # Highlight current chord
        self.chord_display.highlight_chord(current_bar)

    def on_practice_tick(self, timestamp: float, step_index: int):
        """Handle metronome tick for audio feedback."""
        if not self.current_song:
            return

        # Get current pattern (override, section or main song)
        if self.override_pattern_id:
            pattern_id = self.override_pattern_id
        elif self.current_section:
            pattern_id = self.current_section.pattern
        else:
            pattern_id = self.current_song.pattern_id

        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return

        bar_length = pattern.steps_per_bar
        bar_step = step_index % bar_length

        # Play audio feedback
        if bar_step < len(pattern.steps):
            step = pattern.steps[bar_step]

            # Play strum sound
            if step.dir != "-":
                self.audio.play_strum(step.dir, step.accent)

            # Play metronome click with beat awareness
            beats_per_bar = pattern.time_sig[0]
            steps_per_beat = bar_length // beats_per_bar

            if bar_step == 0:
                # Strong beat (downbeat) - use high click
                self.audio.play_click_high()
            elif bar_step % steps_per_beat == 0:
                # Other beats - use accented click
                self.audio.play_click(accent=True)

    def on_metronome_started(self):
        """Handle metronome start."""
        self.transport.set_playing(True)

    def on_metronome_stopped(self):
        """Handle metronome stop."""
        self.transport.set_playing(False)

    def on_step_hit(self, step_index: int):
        """Handle step hit from timeline widget."""
        pass

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Play/Pause - Space bar
        self.play_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.play_shortcut.activated.connect(self.transport.on_play_pause_clicked)

        # Stop - Escape
        self.stop_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.stop_shortcut.activated.connect(self.transport.on_stop_clicked)

        # Section navigation
        self.prev_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.prev_shortcut.activated.connect(self.previous_section)

        self.next_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.next_shortcut.activated.connect(self.next_section)

        # BPM adjustment
        self.bpm_up_shortcut = QShortcut(QKeySequence(Qt.Key_Plus), self)
        self.bpm_up_shortcut.activated.connect(lambda: self.transport.adjust_bpm(5))

        self.bpm_down_shortcut = QShortcut(QKeySequence(Qt.Key_Minus), self)
        self.bpm_down_shortcut.activated.connect(lambda: self.transport.adjust_bpm(-5))

        # Back to menu
        self.back_shortcut = QShortcut(QKeySequence(Qt.ALT | Qt.Key_Left), self)
        self.back_shortcut.activated.connect(self.back_requested.emit)

    def cleanup(self):
        """Cleanup when view is closed."""
        self.metronome.stop()
