import os
import pandas as pd
import shutil
import zipfile
import plotly.express as px
from datetime import datetime

class DatasetManager:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.metadata_csv = os.path.join(self.dataset_path, "metadata.csv")
        self.audio_dir = os.path.join(self.dataset_path, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

    def init_metadata(self):
        if not os.path.exists(self.metadata_csv):
            df = pd.DataFrame(columns=[
                "song_title", "style_prompt", "exclude_style_prompt",
                "audio_file_1", "audio_file_2", "file_format",
                "duration", "model_version", "generation_date",
                "lyrics", "persona", "uploaded_sample"
            ])
            df.to_csv(self.metadata_csv, index=False)

    def log_entry(self, metadata):
        df = pd.read_csv(self.metadata_csv)
        metadata['generation_date'] = datetime.now().isoformat()
        df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
        df.to_csv(self.metadata_csv, index=False)

    def load_metadata(self):
        if os.path.exists(self.metadata_csv):
            return pd.read_csv(self.metadata_csv)
        return pd.DataFrame()

    def visualize(self):
        df = self.load_metadata()
        if df.empty:
            print("No data to visualize.")
            return
        fig = px.bar(df, x='song_title', y='duration', color='style_prompt', title="Audio Dataset Overview")
        fig.show()

    def export_all(self, export_path):
        df = self.load_metadata()
        if df.empty:
            raise ValueError("No data available to export.")

        os.makedirs(export_path, exist_ok=True)
        df.to_csv(os.path.join(export_path, "metadata.csv"), index=False)
        df.to_json(os.path.join(export_path, "metadata.json"), orient='records', indent=2)
        df.to_parquet(os.path.join(export_path, "metadata.parquet"), index=False)

        zip_path = os.path.join(export_path, 'audio_files.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.audio_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.audio_dir)
                    zipf.write(file_path, arcname)
