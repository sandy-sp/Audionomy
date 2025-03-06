# scripts/dataset_manager.py

import os
import pandas as pd
import json
import shutil
import uuid
import datetime
from pydub import AudioSegment
import numpy as np
from scripts.logger import logger

class DatasetManager:
    """Manages dataset metadata, audio files, and versioning."""

    def __init__(self, dataset_path, create_new=False, columns=None):
        self.dataset_path = dataset_path
        self.audio_dir = os.path.join(dataset_path, "audio")
        self.metadata_path = os.path.join(dataset_path, "metadata.csv")
        self.template_path = os.path.join(dataset_path, "dataset.template")
        self.versioning_enabled = True  # Enable dataset versioning

        # Create dataset structure if new
        if create_new:
            os.makedirs(self.dataset_path, exist_ok=True)
            os.makedirs(self.audio_dir, exist_ok=True)

            # Create a dataset template
            if columns:
                self.create_template(columns)

    def create_template(self, columns):
        """Creates a dataset template file with the given columns."""
        template_data = {
            "name": os.path.basename(self.dataset_path),
            "created_at": datetime.datetime.now().isoformat(),
            "columns": columns
        }
        with open(self.template_path, "w") as f:
            json.dump(template_data, f, indent=2)

        # Initialize metadata file
        df = pd.DataFrame(columns=columns)
        df.to_csv(self.metadata_path, index=False)

    def load_metadata(self):
        """Loads dataset metadata from CSV, returning a DataFrame."""
        if os.path.exists(self.metadata_path):
            try:
                return pd.read_csv(self.metadata_path)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return pd.DataFrame()

    def save_metadata(self, df):
        """Saves the DataFrame metadata to CSV with optional versioning."""
        if self.versioning_enabled:
            self._backup_previous_metadata()

        df.to_csv(self.metadata_path, index=False)

    def _backup_previous_metadata(self):
        """Creates a backup of the current metadata before overwriting."""
        if os.path.exists(self.metadata_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.dataset_path, f"metadata_backup_{timestamp}.csv")
            shutil.copy2(self.metadata_path, backup_path)

    def add_audio_files(self, file_paths):
        """Batch imports multiple audio files into the dataset."""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

        metadata = self.load_metadata()
        new_rows = []

        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            # Generate unique filename to avoid conflicts
            original_filename = os.path.basename(file_path)
            file_ext = os.path.splitext(original_filename)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"

            # Copy file to audio directory
            dest_path = os.path.join(self.audio_dir, unique_filename)
            try:
                shutil.copy2(file_path, dest_path)
                audio_info = self.extract_audio_metadata(dest_path)

                # Create new metadata entry
                new_row = {col: "" for col in metadata.columns}
                new_row["filename"] = unique_filename
                new_row.update(audio_info)

                new_rows.append(new_row)
            except Exception as e:
                print(f"Error adding file {file_path}: {e}")

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            metadata = pd.concat([metadata, new_df], ignore_index=True)
            self.save_metadata(metadata)

        return len(new_rows)

    def extract_audio_metadata(self, audio_path):
        """Extracts metadata from an audio file using pydub."""
        try:
            audio = AudioSegment.from_file(audio_path)
            metadata = {
                "duration": len(audio) / 1000,  # Convert ms to seconds
                "file_format": os.path.splitext(audio_path)[1].replace(".", ""),
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "bit_depth": audio.sample_width * 8
            }

            # Calculate additional features if needed
            df = self.load_metadata()
            if df is not None:
                columns = df.columns
                samples = np.array(audio.get_array_of_samples())

                if "rms" in columns:
                    metadata["rms"] = audio.rms
                if "dBFS" in columns:
                    metadata["dBFS"] = audio.dBFS
                if "max_amplitude" in columns:
                    metadata["max_amplitude"] = np.max(np.abs(samples))
                if "min_amplitude" in columns:
                    metadata["min_amplitude"] = np.min(np.abs(samples))

            return metadata
        except Exception as e:
            print(f"Error extracting metadata from {audio_path}: {e}")
            return {
                "duration": 0,
                "file_format": os.path.splitext(audio_path)[1].replace(".", "")
            }

    def update_metadata_value(self, row_index, column_name, new_value):
        """Updates a specific metadata value in the dataset."""
        metadata = self.load_metadata()
        if metadata is None or row_index >= len(metadata):
            return False

        metadata.at[row_index, column_name] = new_value
        self.save_metadata(metadata)
        return True

    def delete_audio_file(self, filename):
        """Deletes an audio file and removes its metadata entry."""
        file_path = os.path.join(self.audio_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        metadata = self.load_metadata()
        if metadata is not None:
            updated_metadata = metadata[metadata["filename"] != filename]
            self.save_metadata(updated_metadata)
            return True
        return False

    def export_dataset(self, destination, format="csv", include_audio=True):
        """Exports the dataset to the specified format."""
        if not os.path.exists(destination):
            os.makedirs(destination)

        metadata = self.load_metadata()
        if metadata is None:
            return False

        # Save metadata in chosen format
        if format.lower() == "csv":
            metadata.to_csv(os.path.join(destination, "metadata.csv"), index=False)
        elif format.lower() == "json":
            metadata.to_json(os.path.join(destination, "metadata.json"), orient="records", indent=2)
        elif format.lower() == "excel":
            metadata.to_excel(os.path.join(destination, "metadata.xlsx"), index=False)

        # Copy audio files if requested
        if include_audio and os.path.exists(self.audio_dir):
            audio_dest = os.path.join(destination, "audio")
            os.makedirs(audio_dest, exist_ok=True)

            for filename in metadata["filename"]:
                src_path = os.path.join(self.audio_dir, filename)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, os.path.join(audio_dest, filename))

        return True

    def log_entry(self, metadata):
        """Logs an entry into the dataset metadata."""
        try:
            df = pd.read_csv(self.metadata_csv)
            df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
            df.to_csv(self.metadata_csv, index=False)
            logger.info(f"New entry added to dataset: {metadata['song_title']}")
        except Exception as e:
            logger.error(f"Failed to log entry: {e}")