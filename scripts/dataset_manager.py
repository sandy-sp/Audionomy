import os
import pandas as pd
import shutil
from datetime import datetime

class DatasetManager:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_path
        self.metadata_csv = os.path.join(dataset_path, "metadata.csv")
        if not os.path.exists(self.metadata_csv):
            self.init_metadata()

    def init_metadata(self):
        columns = ["song_title", "style_prompt", "exclude_style_prompt",
                   "audio_file_1", "audio_file_2", "file_format", "duration",
                   "model_version", "generation_date", "lyrics", "persona", "uploaded_sample"]
        pd.DataFrame(columns=columns).to_csv(self.metadata_csv, index=False)

    def log_entry(self, metadata):
        df = pd.read_csv(self.metadata_csv)
        metadata['generation_date'] = datetime.now().isoformat()
        df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
        df.to_csv(self.metadata_csv, index=False)

    def load_metadata(self):
        return pd.read_csv(self.metadata_csv)

    def export_all(self, export_path):
        df = self.load_metadata()
        df.to_csv(os.path.join(export_path, "metadata.csv"), index=False)
        df.to_json(os.path.join(export_path, "metadata.json"), orient='records', indent=2)
        df.to_parquet(os.path.join(export_path, "metadata.parquet"), index=False)

        # Export audio files as ZIP
        audio_export_path = os.path.join(export_path, "audio_files.zip")
        shutil.make_archive(base_name=audio_zip, format='zip', root_dir=self.dataset_path, base_dir='audio')
