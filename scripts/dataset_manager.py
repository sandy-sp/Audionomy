# scripts/dataset_manager.py

import os
import pandas as pd
import json
import shutil
from pydub import AudioSegment
import numpy as np
import datetime
import uuid

class DatasetManager:
    def __init__(self, dataset_path, create_new=False, columns=None):
        self.dataset_path = dataset_path
        self.audio_dir = os.path.join(dataset_path, "audio")
        self.metadata_path = os.path.join(dataset_path, "metadata.csv")
        self.template_path = os.path.join(dataset_path, "dataset.template")
        
        # Create directories if needed
        if create_new:
            os.makedirs(self.dataset_path, exist_ok=True)
            os.makedirs(self.audio_dir, exist_ok=True)
            
            # Create template file
            if columns:
                template_data = {
                    "name": os.path.basename(dataset_path),
                    "created_at": datetime.datetime.now().isoformat(),
                    "columns": columns
                }
                with open(self.template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)
        
    def init_metadata(self):
        """Initialize an empty metadata file with the columns from the template."""
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r') as f:
                template = json.load(f)
                columns = template.get("columns", [])
                
                # Create empty DataFrame with these columns
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.metadata_path, index=False)
                return True
        return False
    
    def get_metadata(self):
        """Get the dataset metadata as a pandas DataFrame."""
        if os.path.exists(self.metadata_path):
            try:
                return pd.read_csv(self.metadata_path)
            except:
                return None
        return None
    
    def get_template(self):
        """Get the dataset template as a dictionary."""
        if os.path.exists(self.template_path):
            try:
                with open(self.template_path, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def add_audio_files(self, file_paths):
        """Add audio files to the dataset and update metadata."""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
            
        # Load existing metadata
        metadata = self.get_metadata()
        if metadata is None:
            self.init_metadata()
            metadata = self.get_metadata()
            
        if metadata is None:
            return 0
            
        added_count = 0
        new_rows = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
                
            # Generate a unique filename to avoid conflicts
            original_filename = os.path.basename(file_path)
            file_ext = os.path.splitext(original_filename)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            
            # Copy file to audio directory
            dest_path = os.path.join(self.audio_dir, unique_filename)
            try:
                shutil.copy2(file_path, dest_path)
                
                # Extract audio metadata
                audio_info = self.extract_audio_metadata(dest_path)
                
                # Create new row for metadata
                new_row = {col: "" for col in metadata.columns}
                new_row["filename"] = unique_filename
                
                # Add extracted metadata
                for key, value in audio_info.items():
                    if key in metadata.columns:
                        new_row[key] = value
                        
                new_rows.append(new_row)
                added_count += 1
                
            except Exception as e:
                print(f"Error adding file {file_path}: {e}")
                if os.path.exists(dest_path):
                    os.remove(dest_path)
        
        # Update metadata file
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            updated_metadata = pd.concat([metadata, new_df], ignore_index=True)
            updated_metadata.to_csv(self.metadata_path, index=False)
            
        return added_count
    
    def extract_audio_metadata(self, audio_path):
        """Extract metadata from an audio file."""
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # Basic metadata
            metadata = {
                "duration": len(audio) / 1000,  # Convert to seconds
                "file_format": os.path.splitext(audio_path)[1].replace(".", ""),
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "bit_depth": audio.sample_width * 8
            }
            
            # Calculate additional audio features if they exist in the columns
            df = self.get_metadata()
            if df is not None:
                columns = df.columns
                
                if "rms" in columns:
                    metadata["rms"] = audio.rms
                    
                if "dBFS" in columns:
                    metadata["dBFS"] = audio.dBFS
                    
                if "max_amplitude" in columns:
                    samples = np.array(audio.get_array_of_samples())
                    metadata["max_amplitude"] = np.max(np.abs(samples))
                    
                if "min_amplitude" in columns:
                    samples = np.array(audio.get_array_of_samples())
                    metadata["min_amplitude"] = np.min(np.abs(samples))
                    
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata from {audio_path}: {e}")
            return {
                "duration": 0,
                "file_format": os.path.splitext(audio_path)[1].replace(".", "")
            }
    
    def update_metadata_value(self, row_index, column_name, new_value):
        """Update a specific value in the metadata."""
        metadata = self.get_metadata()
        if metadata is None or row_index >= len(metadata):
            return False
            
        metadata.at[row_index, column_name] = new_value
        metadata.to_csv(self.metadata_path, index=False)
        return True
    
    def delete_audio_file(self, filename):
        """Delete an audio file and its metadata entry."""
        # Delete the file
        file_path = os.path.join(self.audio_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Update metadata
        metadata = self.get_metadata()
        if metadata is not None:
            updated_metadata = metadata[metadata["filename"] != filename]
            updated_metadata.to_csv(self.metadata_path, index=False)
            return True
            
        return False
    
    def export_dataset(self, destination, format="csv", include_audio=True):
        """Export the dataset to the specified format."""
        if not os.path.exists(destination):
            os.makedirs(destination)
            
        metadata = self.get_metadata()
        if metadata is None:
            return False
            
        # Export metadata
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
