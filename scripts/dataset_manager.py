import os
import pandas as pd
import json
from pydub.utils import mediainfo
from datetime import datetime
import shutil
import zipfile

class DatasetManager:
    def __init__(self, dataset_path, create_new=False, columns=None):
        self.dataset_path = dataset_path
        self.metadata_csv = os.path.join(self.dataset_path, "metadata.csv")
        self.audio_dir = os.path.join(self.dataset_path, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

        if create_new and columns:
            self.create_template(columns)
        self.template = self.load_template()

    def get_template_path(self):
        for file in os.listdir(self.dataset_path):
            if file.endswith('.template'):
                return os.path.join(self.dataset_path, file)
        return None

    def load_template(self):
        template_path = self.get_template_path()
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError("Dataset template file not found.")

    def create_template(self, columns):
        template_data = {
            "columns": columns,
            "created_at": datetime.now().isoformat(),
            "source": "Audionomy User Template"
        }
        template_file = os.path.join(
            self.dataset_path, f"{os.path.basename(self.dataset_path)}.template"
        )
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)

    def init_metadata(self):
        if not self.template:
            raise ValueError("No template loaded. Cannot initialize metadata.")
        df = pd.DataFrame(columns=self.template["columns"])
        df.to_csv(self.metadata_csv, index=False)

    def log_entry(self, metadata):
        if not os.path.exists(self.metadata_csv):
            self.init_metadata()
        df = pd.read_csv(self.metadata_csv)
        metadata['generation_date'] = datetime.now().isoformat()
        df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
        df.to_csv(self.metadata_csv, index=False)

    def autofill_audio_metadata(self, audio_file):
        info = mediainfo(audio_file)
        return {
            "file_format": info.get('format_name'),
            "duration": round(float(info.get('duration', 0)), 2)
        }

    def export_dataset(self, export_path):
        os.makedirs(export_path, exist_ok=True)

        # Export metadata
        df = pd.read_csv(self.metadata_csv)
        df.to_csv(os.path.join(export_path, 'metadata.csv'), index=False)
        df.to_json(os.path.join(export_path, 'metadata.json'), orient='records', indent=2)
        df.to_parquet(os.path.join(export_path, 'metadata.parquet'), index=False)

        # Export audio files in ZIP
        zip_path = os.path.join(export_path, "audio_files.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.audio_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.audio_dir)
                    zipf.write(file_path, arcname)