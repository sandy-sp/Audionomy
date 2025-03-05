import pandas as pd
import os
from datetime import datetime

DATASET_CSV = "metadata.csv"

def init_csv(csv_path):
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=[
            "song_title", "style_prompt", "exclude_style_prompt",
            "audio_file_1", "audio_file_2", "file_format",
            "duration", "model_version", "generation_date",
            "lyrics", "persona", "uploaded_sample"
        ])
        df.to_csv(csv_path, index=False)

def log_metadata(metadata: dict, csv_path="metadata.csv"):
    df = pd.read_csv(csv_path)
    metadata['generation_date'] = datetime.now().isoformat()
    df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
    df.to_csv(csv_path, index=False)

# Usage Example:
if __name__ == "__main__":
    metadata_example = {
        "song_title": "Evening Breeze",
        "style_prompt": "Ambient",
        "exclude_style_prompt": "Vocals",
        "audio_file_1": "audio/evening_breeze_v1.mp3",
        "audio_file_2": "audio/evening_breeze_v2.mp3",
        "file_format": "mp3",
        "duration": 180,
        "model_version": "suno-2.1",
        "generation_date": "2025-03-05",
        "lyrics": "",
        "persona": "",
        "uploaded_sample": ""
    }

    csv_path = "metadata.csv"
    init(csv_path)
    log_metadata(metadata_example, csv_path)
