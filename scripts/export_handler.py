# scripts/export_handler.py

import os
import pandas as pd
import json
import shutil
import zipfile
import subprocess
from datasets import Dataset, DatasetDict
from PySide6.QtCore import QThread, Signal


class ExportHandler:
    """Handles dataset export to local and cloud destinations."""

    def __init__(self, dataset_path, export_options):
        self.dataset_path = dataset_path
        self.metadata_path = os.path.join(dataset_path, "metadata.csv")
        self.audio_dir = os.path.join(dataset_path, "audio")
        self.export_options = export_options
        self.destination = export_options.get("destination")
        self.format = export_options.get("format")
        self.include_audio = export_options.get("include_audio", True)
        self.cloud_service = export_options.get("service")

    def execute_export(self):
        """Determines the appropriate export method."""
        try:
            logger.info(f"Starting dataset export: {self.dataset_path}")
            if self.cloud_service:
                return self.export_to_cloud()
            else:
                return self.export_to_local()
        except Exception as e:
            logger.critical(f"Export failed: {e}")
            return False, f"Export failed: {e}"

    def export_to_local(self):
        """Exports the dataset to a local folder."""
        os.makedirs(self.destination, exist_ok=True)

        # Load metadata
        df = pd.read_csv(self.metadata_path)

        # Export metadata
        if self.format == "CSV":
            df.to_csv(os.path.join(self.destination, "metadata.csv"), index=False)
        elif self.format == "JSON":
            df.to_json(os.path.join(self.destination, "metadata.json"), orient="records", indent=2)
        elif self.format == "Parquet":
            df.to_parquet(os.path.join(self.destination, "metadata.parquet"), index=False)
        elif self.format == "ZIP Archive":
            self._export_as_zip(df)

        # Copy audio files if needed
        if self.include_audio and os.path.exists(self.audio_dir):
            audio_dest = os.path.join(self.destination, "audio")
            os.makedirs(audio_dest, exist_ok=True)
            for filename in df["filename"]:
                src_path = os.path.join(self.audio_dir, filename)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, os.path.join(audio_dest, filename))

        return True, f"Dataset exported successfully to {self.destination}"

    def _export_as_zip(self, df):
        """Exports dataset as a ZIP archive."""
        zip_filename = os.path.join(self.destination, "dataset.zip")
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add metadata files
            df.to_csv("metadata.csv", index=False)
            zipf.write("metadata.csv", "metadata.csv")
            os.remove("metadata.csv")

            # Add audio files
            if self.include_audio:
                for filename in df["filename"]:
                    file_path = os.path.join(self.audio_dir, filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.join("audio", filename))

    def export_to_cloud(self):
        """Exports dataset to the selected cloud service."""
        if self.cloud_service == "Hugging Face":
            return self.export_to_huggingface()
        elif self.cloud_service == "GitHub":
            return self.export_to_github()
        elif self.cloud_service == "Kaggle":
            return self.export_to_kaggle()
        else:
            return False, "Invalid cloud service selection."

    def export_to_huggingface(self):
        """Exports dataset to Hugging Face Datasets."""
        df = pd.read_csv(self.metadata_path)
        dataset = Dataset.from_pandas(df)
        dataset_dict = DatasetDict({"train": dataset})

        repo_name = self.export_options.get("repo_name")
        if not repo_name:
            return False, "Missing Hugging Face repository name."

        try:
            dataset_dict.push_to_hub(repo_name)
            return True, f"Dataset exported to Hugging Face repository: {repo_name}"
        except Exception as e:
            return False, f"Hugging Face export failed: {e}"

    def export_to_github(self):
        """Exports dataset to a GitHub repository."""
        repo_name = self.export_options.get("repo_name")
        if not repo_name:
            return False, "Missing GitHub repository name."

        repo_url = f"https://github.com/{repo_name}.git"
        export_folder = os.path.join(self.dataset_path, "github_export")
        os.makedirs(export_folder, exist_ok=True)

        try:
            shutil.copy2(self.metadata_path, os.path.join(export_folder, "metadata.csv"))
            if self.include_audio and os.path.exists(self.audio_dir):
                shutil.copytree(self.audio_dir, os.path.join(export_folder, "audio"), dirs_exist_ok=True)

            subprocess.run(["git", "init"], cwd=export_folder, check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=export_folder, check=True)
            subprocess.run(["git", "add", "."], cwd=export_folder, check=True)
            subprocess.run(["git", "commit", "-m", "Initial dataset upload"], cwd=export_folder, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=export_folder, check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=export_folder, check=True)

            return True, f"Dataset exported to GitHub repository: {repo_name}"
        except Exception as e:
            logger.error(f"GitHub export failed: {e}")
            return False, f"GitHub export failed: {e}"

    def export_to_kaggle(self):
        """Exports dataset to Kaggle."""
        dataset_slug = self.export_options.get("dataset_slug")
        title = self.export_options.get("title")
        if not dataset_slug or not title:
            return False, "Missing Kaggle dataset slug or title."

        export_folder = os.path.join(self.dataset_path, "kaggle_export")
        os.makedirs(export_folder, exist_ok=True)

        shutil.copy2(self.metadata_path, os.path.join(export_folder, "metadata.csv"))

        if self.include_audio and os.path.exists(self.audio_dir):
            shutil.copytree(self.audio_dir, os.path.join(export_folder, "audio"), dirs_exist_ok=True)

        # Create Kaggle metadata file
        metadata = {
            "title": title,
            "id": dataset_slug,
            "licenses": [{"name": "CC0-1.0"}]
        }

        with open(os.path.join(export_folder, "dataset-metadata.json"), "w") as f:
            json.dump(metadata, f)

        # Push to Kaggle
        try:
            subprocess.run(["kaggle", "datasets", "create", "-p", export_folder, "-u"], check=True)
            return True, f"Dataset exported to Kaggle: {dataset_slug}"
        except Exception as e:
            return False, f"Kaggle export failed: {e}"
