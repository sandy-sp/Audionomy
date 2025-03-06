# scripts/audio_processing.py

import os
import numpy as np
import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt
from pydub import AudioSegment
import essentia.standard as es
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from PySide6.QtCore import QThread, Signal
from scripts.logger import logger


class AudioProcessor:
    """Handles audio feature extraction, normalization, format conversion, and visualization."""

    SUPPORTED_FORMATS = ["wav", "mp3", "flac", "ogg"]

    def __init__(self, normalize=False, target_format="wav"):
        self.normalize = normalize
        self.target_format = target_format.lower()

    def process_audio_file(self, file_path, output_dir=None):
        """Processes a single audio file: extracts features, normalizes, and converts format."""
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return None, None

        try:
            logger.info(f"Processing audio file: {file_path}")
            audio, sr = librosa.load(file_path, sr=None)
            metadata = self.extract_metadata(file_path, audio, sr)

            if self.normalize:
                audio = self.normalize_audio(audio)
                logger.debug(f"Audio normalized: {file_path}")

            converted_path = file_path
            if self.target_format and self.get_file_extension(file_path) != self.target_format:
                converted_path = self.convert_audio(file_path, self.target_format, output_dir)
                logger.info(f"Converted {file_path} to {converted_path}")

            return metadata, converted_path
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None, None

    def extract_metadata(self, file_path, audio, sr):
        """Extracts audio metadata including pitch, tempo, loudness, and tags."""
        duration = librosa.get_duration(y=audio, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        pitch = librosa.yin(audio, fmin=50, fmax=5000, sr=sr)
        avg_pitch = np.mean(pitch) if len(pitch) > 0 else None

        # Extract metadata using Mutagen
        mutagen_data = self.extract_metadata_tags(file_path)

        # Extract loudness using Essentia
        loudness = self.extract_loudness(file_path)

        return {
            "filename": os.path.basename(file_path),
            "duration": round(duration, 2),
            "sample_rate": sr,
            "tempo": round(tempo, 2),
            "pitch": round(avg_pitch, 2) if avg_pitch else None,
            "bit_depth": self.get_bit_depth(file_path),
            "channels": self.get_channels(file_path),
            "file_format": self.get_file_extension(file_path),
            "loudness": round(loudness, 2) if loudness else None,
            "artist": mutagen_data.get("artist", ""),
            "album": mutagen_data.get("album", ""),
            "title": mutagen_data.get("title", ""),
        }

    def extract_metadata_tags(self, file_path):
        """Extracts metadata tags (artist, album, title) using Mutagen."""
        try:
            if file_path.endswith(".mp3"):
                audio = MP3(file_path)
            elif file_path.endswith(".flac"):
                audio = FLAC(file_path)
            elif file_path.endswith(".ogg"):
                audio = OggVorbis(file_path)
            else:
                return {}

            return {
                "artist": audio.get("TPE1", [""])[0],
                "album": audio.get("TALB", [""])[0],
                "title": audio.get("TIT2", [""])[0],
            }
        except Exception as e:
            logger.warning(f"Failed to extract metadata tags for {file_path}: {e}")
            return {}

    def generate_waveform(self, file_path, output_path):
        """Generates and saves a waveform plot of the audio file."""
        audio, sr = librosa.load(file_path, sr=None)
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(audio, sr=sr, alpha=0.8)
        plt.title("Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.savefig(output_path)
        plt.close()

    def generate_spectrogram(self, file_path, output_path):
        """Generates and saves a spectrogram of the audio file."""
        audio, sr = librosa.load(file_path, sr=None)
        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr)
        log_spectrogram = librosa.power_to_db(spectrogram, ref=np.max)

        plt.figure(figsize=(10, 4))
        librosa.display.specshow(log_spectrogram, sr=sr, x_axis="time", y_axis="mel")
        plt.title("Spectrogram")
        plt.colorbar(format="%+2.0f dB")
        plt.savefig(output_path)
        plt.close()

    def normalize_audio(self, audio):
        """Normalizes an audio signal to a target peak level."""
        return librosa.util.normalize(audio)

    def convert_audio(self, file_path, target_format, output_dir=None):
        """Converts audio to the specified format."""
        if target_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {target_format}")

        output_dir = output_dir or os.path.dirname(file_path)
        output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        audio = AudioSegment.from_file(file_path)
        audio.export(output_path, format=target_format)
        return output_path


class AudioProcessingWorker(QThread):
    """Handles batch audio processing in a separate thread."""

    progress_updated = Signal(int)
    processing_complete = Signal(list)

    def __init__(self, file_paths, output_dir, normalize=True, target_format="wav"):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.processor = AudioProcessor(normalize=normalize, target_format=target_format)

    def run(self):
        """Processes audio files in batch mode with threading."""
        results = []
        total_files = len(self.file_paths)

        for i, file_path in enumerate(self.file_paths):
            try:
                metadata, converted_path = self.processor.process_audio_file(file_path, self.output_dir)
                results.append({"metadata": metadata, "converted_path": converted_path})
                progress = int(((i + 1) / total_files) * 100)
                self.progress_updated.emit(progress)
            except Exception as e:
                logger.warning(f"Skipping file due to error: {file_path} - {e}")

        self.processing_complete.emit(results)