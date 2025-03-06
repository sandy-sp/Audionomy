# scripts/audio_processing.py

import os
import numpy as np
import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt
from pydub import AudioSegment
from PySide6.QtCore import QThread, Signal


class AudioProcessor:
    """Handles audio feature extraction, normalization, and format conversion."""

    SUPPORTED_FORMATS = ["wav", "mp3", "flac", "ogg"]

    def __init__(self, normalize=False, target_format="wav"):
        self.normalize = normalize
        self.target_format = target_format.lower()

    def process_audio_file(self, file_path, output_dir=None):
        """Processes a single audio file: extracts features, normalizes, and converts format."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Load audio file
        audio, sr = librosa.load(file_path, sr=None)
        metadata = self.extract_metadata(file_path, audio, sr)

        # Normalize audio
        if self.normalize:
            audio = self.normalize_audio(audio)

        # Convert format if needed
        converted_path = file_path
        if self.target_format and self.get_file_extension(file_path) != self.target_format:
            converted_path = self.convert_audio(file_path, self.target_format, output_dir)

        return metadata, converted_path

    def process_audio_batch(self, file_paths, output_dir=None):
        """Processes a batch of audio files."""
        results = []
        for file_path in file_paths:
            try:
                metadata, converted_path = self.process_audio_file(file_path, output_dir)
                results.append({"metadata": metadata, "converted_path": converted_path})
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        return results

    def extract_metadata(self, file_path, audio, sr):
        """Extracts audio metadata such as duration, sample rate, and amplitude features."""
        duration = librosa.get_duration(y=audio, sr=sr)
        rms = np.sqrt(np.mean(audio ** 2))
        dBFS = librosa.amplitude_to_db(np.abs(audio), ref=np.max)
        avg_dBFS = np.mean(dBFS)

        return {
            "filename": os.path.basename(file_path),
            "duration": round(duration, 2),
            "sample_rate": sr,
            "rms": round(rms, 4),
            "dBFS": round(avg_dBFS, 2),
            "bit_depth": self.get_bit_depth(file_path),
            "channels": self.get_channels(file_path),
            "file_format": self.get_file_extension(file_path),
        }

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

    @staticmethod
    def get_file_extension(file_path):
        """Returns the file extension (format) of the given audio file."""
        return os.path.splitext(file_path)[1].lower().replace(".", "")

    @staticmethod
    def get_bit_depth(file_path):
        """Returns the bit depth of the audio file."""
        try:
            info = sf.info(file_path)
            return info.subtype_info.split(" ")[0] if info.subtype_info else "Unknown"
        except:
            return "Unknown"

    @staticmethod
    def get_channels(file_path):
        """Returns the number of audio channels."""
        try:
            return AudioSegment.from_file(file_path).channels
        except:
            return "Unknown"


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
                print(f"Error processing {file_path}: {e}")

        self.processing_complete.emit(results)
