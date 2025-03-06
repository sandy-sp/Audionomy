import os
import pandas as pd
import json
from pydub.utils import mediainfo
from datetime import datetime

class DatasetManager:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.metadata_csv = os.path.join(self.dataset_path, "metadata.csv")
        self.audio_dir = os.path.join(self.dataset_path, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)
        self.template = self.load_template()

    def get_template_path(self):
        for file in os.listdir(self.dataset_path):
            if file.endswith('.template'):
                return os.path.join(self.dataset_path, file)
        return None

    def create_template(self, columns):
        template_data = {
            "columns": columns,
            "created_at": datetime.now().isoformat(),
            "source": "Audionomy User Template"
        }
        template_file = os.path.join(self.dataset_path, f"{os.path.basename(self.dataset_path)}.template")
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)

    def init_metadata(self):
        with open(self.get_template_path()) as f:
            template = json.load(f)
        df = pd.DataFrame(columns=template["columns"])
        df.to_csv(self.metadata_csv, index=False)

    def log_entry(self, metadata):
        df = pd.read_csv(self.metadata_csv)
        metadata['generation_date'] = datetime.now().isoformat()
        df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
        df.to_csv(self.metadata_csv, index=False)

    def autofill_audio_metadata(self, audio_file_path):
        info = mediainfo(audio_file)
        return {
            "file_format": info.get('format_name'),
            "duration": round(float(info.get('duration', 0)), 2)
        }
