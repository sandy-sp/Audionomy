import os
import pandas as pd
import json
from pydub.utils import mediainfo
from datetime import datetime
import shutil
import zipfile
from datasets import Dataset, DatasetDict
import subprocess

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

        df = pd.read_csv(self.metadata_csv)

        # Export metadata
        df.to_csv(os.path.join(export_path, 'metadata.csv'), index=False)
        df.to_json(os.path.join(export_path, 'metadata.json'), orient='records', indent=2)
        df.to_parquet(os.path.join(export_path, 'metadata.parquet'), index=False)

        # Export audio files
        audio_zip = os.path.join(export_path, 'audio_files.zip')
        with zipfile.ZipFile(audio_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.audio_dir):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        arcname=os.path.relpath(os.path.join(root, file), self.audio_dir)
                    )

    def export_to_huggingface(self, repo_name, split='train'):
        df = pd.read_csv(self.metadata_csv)
        if df.empty:
            raise ValueError("Dataset is empty, nothing to export.")

        dataset = Dataset.from_pandas(df)

        dataset_dict = DatasetDict({split: dataset})
        dataset_dict.push_to_hub(repo_name)

    def export_to_kaggle(self, dataset_slug, title):
        export_folder = os.path.join(self.dataset_path, "kaggle_export")
        self.export_dataset(export_folder)

        # Create Kaggle metadata file
        metadata = {
            "title": title,
            "id": dataset_slug,
            "licenses": [{"name": "CC0-1.0"}]
        }

        with open(os.path.join(export_folder, "dataset-metadata.json"), 'w') as f:
            json.dump(metadata, f)

        # Push to Kaggle
        subprocess.run(["kaggle", "datasets", "create", "-p", export_folder, "-u"], check=True)