import os
import pandas as pd
import json

class DatasetManager:
    def __init__(self, path):
        self.dataset_path = path
        self.template_path = self.get_template_path()

    def get_template_path(self):
        for file in os.listdir(self.dataset_path):
            if file.endswith('.template'):
                return os.path.join(self.dataset_path, file)
        return None

    def create_template(self, columns=None):
        template = {"columns": columns or ["song_title", "style_prompt", "duration"]}
        template_name = f"{os.path.basename(self.dataset_path)}.template"
        with open(os.path.join(self.dataset_path, template_name), "w") as f:
            json.dump(template, f, indent=2)

    def init_metadata(self):
        with open(self.template_path) as f:
            template = json.load(f)
        df = pd.DataFrame(columns=template["columns"])
        df.to_csv(os.path.join(self.dataset_path, "metadata.csv"), index=False)
