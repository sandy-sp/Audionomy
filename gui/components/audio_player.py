# gui/components/audio_player.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import qtawesome as qta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pydub import AudioSegment
import io
import tempfile
import os

class AudioWaveformWidget(QWidget):
    playbackPositionChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.audio_path = None
        self.setup_ui()
        self.setup_player()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Waveform visualization
        self.figure, self.ax = plt.subplots(figsize=(10, 2))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(100)
        layout.addWidget(self.canvas)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton(qta.icon("fa5s.play"), "")
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.position_slider)
        
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
    def setup_player(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.update_play_button)
        
    def load_audio(self, audio_path):
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False
            
        self.audio_path = audio_path
        self.player.setSource(QUrl.fromLocalFile(audio_path))
        
        try:
            # Load audio data for visualization
            audio = AudioSegment.from_file(audio_path)
            samples = np.array(audio.get_array_of_samples())
            
            # Normalize for visualization
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)
            
            self.audio_data = samples
            self.plot_waveform()
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False
            
    def plot_waveform(self):
        if self.audio_data is None:
            return
            
        self.ax.clear()
        
        # Downsample for better performance if needed
        if len(self.audio_data) > 10000:
            samples = self.audio_data[::len(self.audio_data)//10000]
        else:
            samples = self.audio_data
            
        # Plot waveform
        self.ax.plot(samples, color='#3498db', linewidth=0.5)
        self.ax.set_ylim([-32768, 32768])
        self.ax.set_xlim([0, len(samples)])
        self.ax.axis('off')
        
        # Add position marker
        self.position_line = self.ax.axvline(0, color='#e74c3c', linewidth=1)
        
        self.canvas.draw()
        
    def toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()
            
    def update_play_button(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(qta.icon("fa5s.pause"))
        else:
            self.play_button.setIcon(qta.icon("fa5s.play"))
            
    def set_position(self, position):
        if self.player.duration() > 0:
            position_ms = int(position / 100.0 * self.player.duration())
            self.player.setPosition(position_ms)
            
            # Update waveform position marker
            if self.audio_data is not None:
                position_sample = int(position / 100.0 * len(self.audio_data))
                self.position_line.set_xdata(position_sample)
                self.canvas.draw_idle()
            
    def update_position(self, position):
        if self.player.duration() > 0:
            position_percent = position / self.player.duration() * 100
            self.position_slider.setValue(int(position_percent))
            
            # Update time label
            current = self.format_time(position)
            total = self.format_time(self.player.duration())
            self.time_label.setText(f"{current} / {total}")
            
            # Update waveform position marker
            if self.audio_data is not None:
                position_sample = int(position / self.player.duration() * len(self.audio_data))
                self.position_line.set_xdata(position_sample)
                self.canvas.draw_idle()
                
            self.playbackPositionChanged.emit(position)
            
    def update_duration(self, duration):
        self.position_slider.setRange(0, 100)
        total = self.format_time(duration)
        current = self.format_time(0)
        self.time_label.setText(f"{current} / {total}")
        
    def format_time(self, ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"
        
    def stop(self):
        self.player.stop()
        
    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)
