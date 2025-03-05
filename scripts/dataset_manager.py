import os
import pandas as pd
import shutil
import zipfile

class DatasetManager:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.metadata_file = os.path.join(dataset_path, "metadata.csv")

    def init_metadata(self):
        if not os.path.exists(self.metadata_path()):
            pd.DataFrame(columns=[
                "song_title", "style_prompt", "exclude_style_prompt",
                "audio_file_1", "audio_file_2", "file_format",
                "duration", "model_version", "generation_date",
                "lyrics", "persona", "uploaded_sample"
            ]).to_csv(self.metadata_csv_path(), index=False)

    def metadata_csv_path(self):
        return os.path.join(self.dataset_path, "metadata.csv")

    def load_metadata(self):
        return pd.read_csv(self.metadata_csv_path())

    def metadata_csv_path(self):
        return os.path.join(self.dataset_path, "metadata.csv")

    def export_all(self, export_path):
        df = self.load_metadata()
        df.to_csv(os.path.join(export_path, "metadata.csv"), index=False)
        df.to_json(os.path.join(export_path, "metadata.json"), orient='records', indent=2)
        df.to_parquet(os.path.join(export_path, "metadata.parquet"), index=False)

        audio_dir = os.path.join(self.dataset_path, 'audio')
        zip_path = os.path.join(export_path, 'audio_files.zip')

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(audio_dir := os.path.join(self.dataset_path, "audio")):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, audio_dir)
                    zip_file.write(file_path, arcname)
